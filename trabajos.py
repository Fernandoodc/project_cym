from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import Form, status
from typing import List
from fastapi import UploadFile, File
from fastapi import Depends
from fastapi.responses import RedirectResponse
from manager import manager
from mongo import find_one, update_one, find_one_and_update, insert_one
from bson import json_util, ObjectId
from datetime import datetime, timedelta
from models import aprovacion, datosProduccion, perdida
from json import loads
from functions import trabajos, insumos
from config import settings
Trabajos = APIRouter()
templates = Jinja2Templates(directory="templates")

@Trabajos.get("/orden_trabajo")
async def pedidos(request: Request, codProduccion:str='',  user=Depends(manager)):
    data = trabajos.trabajos()
    return templates.TemplateResponse("orden_trabajo.html", context={"request": request, 'trabajos': data, 'codProduccion': codProduccion, 'userInfo': user})

@Trabajos.get("/info_produccion/{cod}")
def infoProduccion(cod: str, user=Depends(manager)):
    data = json_util._json_convert(trabajos.infoProduccion(cod))
    return data

@Trabajos.get('/estado_produccion')
async def estadoProduccion(response: Response, codPedido: str,  user=Depends(manager)):
    data = json_util._json_convert(trabajos.estadoProduccionPedido(codPedido))
    return data

@Trabajos.post("/upload_disenio")
async def uploadDisenio(response : Response ,files: List[UploadFile] = File(...), cod_pedido: str = Form(...), cod_detalle: str = Form(...), user=Depends(manager)):
    return files

@Trabajos.get("/produccion/{cod}")
async def produccion(request: Request, cod:str, user=Depends(manager)):
    info = find_one('produccion', {'codProduccion': cod, 'aprovado': True})
    info = json_util._json_convert(info)
    #if info == None or info['etapa']['codEtapa'] == 2:
    if info == None:
        return RedirectResponse('/')
    if info['etapa']['codEtapa'] == 0 or info['etapa']['codEtapa'] == 3:
        #await update_one('produccion', {'codProduccion': cod}, {'$set': {'etapa.codEtapa': 1, 'etapa.descripcion': 'Iniciado'}})
        band = await trabajos.iniciarProduccion(cod)
        if not band:
            data = trabajos.trabajos()
            msg = 'No hay insumos suficientes para iniciar la producción'
            return templates.TemplateResponse("orden_trabajo.html", context={"request": request, 'trabajos': data, 'msg': msg, "userInfo": user})
    #producto = trabajos.detalleProduccion(info['detallesPedidos_id']['$oid'])
    producto = trabajos.detalleProduccion(cod)
    insumosPerdidos = insumos.insumosPerdidos(cod)
    return templates.TemplateResponse("produccion.html", context={'request': request, "producto": producto, 'insumosPerdidos': insumosPerdidos ,"userInfo": user})

@Trabajos.put('/produccion/cancelar')
async def cancelarProducion(response: Response, codProduccion: str, user=Depends(manager)):
    await update_one('produccion', {'codProduccion': codProduccion}, {'$set': {'etapa.codEtapa': 0, 'etapa.descripcion': 'No Iniciado'}})
    await insumos.reponerStock(codProduccion)
    return {'msg': 'success'}

@Trabajos.put('/produccion/pausar')
async def cancelarProducion(response: Response, codProduccion: str, user=Depends(manager)):
    await update_one('produccion', {'codProduccion': codProduccion}, {'$set': {'etapa.codEtapa': 3, 'etapa.descripcion': 'Pausado'}})
    await insumos.reponerStock(codProduccion)
    return {'msg': 'success'}
@Trabajos.post("/act_aprovacion")
async def actAprovacion(response: Response, estado: aprovacion, user=Depends(manager)):
    #await update_one("produccion", {"codProduccion": estado.codProduccion}, {"aprovado": estado.estado})
    await find_one_and_update("produccion", {"codProduccion": estado.codProduccion}, {"aprovado": estado.estado})
    return "success"
4
@Trabajos.post("/produccion/procesar", status_code=status.HTTP_200_OK)
async def procesar(response: Response, datos: datosProduccion, user=Depends(manager)):
    await update_one('produccion', {'codProduccion': datos.codProduccion}, {'$inc': {'cantidadRestante': -datos.cantidad}})
    produccion = json_util._json_convert(find_one('produccion', {'codProduccion': datos.codProduccion}))
    print(produccion)
    pedido = json_util._json_convert(find_one('detallesPedidos', {'_id': ObjectId(produccion['detallesPedidos_id']['$oid'])}))
    cantidad = {
        'cantidad': pedido['cantidad'],
        'cantidadRestante': produccion['cantidadRestante']
    }
    print(produccion['cantidadRestante'])
    if produccion['cantidadRestante']<=0:
        await update_one('produccion', {'codProduccion': datos.codProduccion}, {"$set": {'etapa.codEtapa': 2, 'etapa.descripcion': 'Terminado'}})
    return cantidad

@Trabajos.post('/produccion/solicitar_insumos', status_code=status.HTTP_200_OK)
async def informarPerdida(response: Response, datos:perdida, user=Depends(manager)):
    insumo = json_util._json_convert(find_one('insumos', {'codInsumo': datos.codInsumo}))
    print(insumo['stock'], " - ", datos.cantidad)
    if insumo['stock']>=datos.cantidad:
        empleado = json_util._json_convert(find_one('usuarios', {'username': user.username}))
        infoPerdida = {
            "comentarios": datos.comentarios,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "cantidad": datos.cantidad,
            "Produccion_id": datos.codProduccion,
            "Insumos_id": datos.codInsumo,
            "datosEmpleado": {
                "Usuarios_id": ObjectId(empleado['_id']['$oid']),
                "Nombre": empleado['nombre'],
                "Apellido": empleado['apellido'],
                "Celular": empleado['celular'],
                "Email": empleado['email']
            }
        }
        insert_one('insumosPerdidos', infoPerdida)
        await update_one('insumos', {'codInsumo': datos.codInsumo}, {'$inc': {'stock': -datos.cantidad}})
        return {'msg': 'success'}
    return False
        
