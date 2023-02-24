from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from manager import manager
from mongo import insert_one, filter, find
from pymongo import MongoClient, ReturnDocument
from config import settings
from bson import json_util, ObjectId
from datetime import datetime, timedelta
from json import loads
from models import productos
from functions import infoProductos
Productos = APIRouter()
templates = Jinja2Templates(directory="templates")
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
@Productos.get("/productos")
async def listaDeProductos(request: Request, user=Depends(manager)):
    productos = db['productos'].find()
    return templates.TemplateResponse('productos.html', context={'request': request, 'userInfo': user ,'productos': productos})

@Productos.get("/nuevo_producto")
async def nuevoProducto(request: Request, user=Depends(manager)):
    insumos = db['insumos'].find({'tipoInsumo_id': { '$ne': 3 }})
    return templates.TemplateResponse("nuevo_producto.html", context={'request': request, 'insumos': insumos, 'userInfo': user})

@Productos.post("/agregar_producto")
async def agregarProducto(response: Response, producto: productos, user=Depends(manager)):
    for i in range(0, len(producto.preciosMayoristas)):
        for j in range(0, len(producto.preciosMayoristas)-1):
            if producto.preciosMayoristas[j].cantidad > producto.preciosMayoristas[(j+1)].cantidad:
                aux = producto.preciosMayoristas[j]
                producto.preciosMayoristas[j] = producto.preciosMayoristas[j+1]
                producto.preciosMayoristas[j+1] = aux
    seq = db['seq'].find_one_and_update({"cod": 4}, {"$inc":{"seq": 1}}, upsert=True , return_document=ReturnDocument.AFTER)
    cod = '0'*(settings.COD_PRODUCTOS - len(str(seq['seq']))) + str(seq["seq"])
    producto.codProducto = cod
    db['productos'].insert_one(loads(producto.json()))
    return cod

@Productos.get("/editar_producto/{cod}")
async def editar(request: Request, cod:str, user=Depends(manager)):
    insumos = db['insumos'].find()
    producto = json_util._json_convert(infoProductos.infoProducto(cod))
    insumosProducto = infoProductos.infoInsumos(cod)
    return templates.TemplateResponse("editar_producto.html", context={'request': request, 'insumos': insumos, 'producto': producto, 'insumosProducto': insumosProducto , 'userInfo': user})

@Productos.post("/editar_producto")
async def editarProducto(response: Response, producto: productos, user=Depends(manager)):
    if filter('productos', {'codProducto': producto.codProducto}) == None:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    anterior = db['productos'].find_one({'codProducto': producto.codProducto})
    nuevo = loads(producto.json())
    usuario_id = db['usuarios'].find_one({'username': user.username})
    datosAuditoria = {
        'fecha': datetime.now().strftime("%y-%m-%d %H:%M"),
        'usuario': usuario_id['_id'],
        'codProducto': producto.codProducto,
        'accion': 'editar',
        'anterior': anterior,
        'cambios': nuevo
    }
    db['auditoriaProductos'].insert_one(datosAuditoria)
    db['productos'].update_one({'codProducto': producto.codProducto}, {'$set':loads(producto.json())})

@Productos.post('/eliminar_producto')
async def eliminarProducto(response: Response, codProducto: str, user=Depends(manager)):
    usuario_id = db['usuarios'].find_one({'username': user.username})
    anterior = db['productos'].find_one({'codProducto': codProducto})
    if infoProductos.controlDelete(codProducto) == False:
        response.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Aún existen pedidos sin entregar o terminar con este producto, no se puede eliminar'}
    datos = {
        'codProducto': codProducto,
        'fecha': datetime.now().strftime("%y-%m-%d %H:%M"),
        'usuario': usuario_id['_id'],
        'accion': 'eliminar',
        'anterior': anterior,
    }
    db['auditoriaProductos'].insert_one(datos)
    db['productos'].delete_one({'codProducto': codProducto})
    return {'msg': 'deleted'}
