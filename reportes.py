from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import Depends
from bson import json_util
from pymongo import MongoClient
import datetime
from manager import	 manager
from functions import infoPedidos, trabajos, funcionesReportes, usuarios
from config import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
Reportes = APIRouter()
pedidos = funcionesReportes.Pedidos()
insumos = funcionesReportes.Insumos()

templates = Jinja2Templates(directory="templates")

UPermitidos = [1]

@Reportes.get('/pedidos/sin_entregar')
async def sinEntregar(request: Request, fInicio:str='', fFin:str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if fInicio == '':
        fInicio = datetime.datetime.now() - datetime.timedelta(days=30)
        fInicio = fInicio.strftime("%Y-%m-%d")
    if fFin == '':
        fFin = datetime.datetime.now().strftime("%Y-%m-%d")
    data = json_util._json_convert(pedidos.noEntregados(fInicio, fFin))
    return templates.TemplateResponse('no_entregados.html', context={'request': request,'pedidos': data, 'fInicio': fInicio, 'fFin': fFin, 'userInfo': user})

@Reportes.get('/pedidos/resumen')
async def resumenPedidos(request: Request, fInicio:str='', fFin:str='', codEntrega: int = 0, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if fInicio == '':
        fInicio = datetime.datetime.now() - datetime.timedelta(days=30)
        fInicio = fInicio.strftime("%Y-%m-%d")
    if fFin == '':
        fFin = datetime.datetime.now().strftime("%Y-%m-%d")
    data = json_util._json_convert(pedidos.resumen(fInicio, fFin, codEntrega))
    return templates.TemplateResponse('resumen_pedidos.html', context={'request': request, 'productos': data, 'fInicio': fInicio, 'fFin': fFin, 'codEntrega': codEntrega, 'userInfo': user})

@Reportes.get('/insumos/perdidos_detalles')
async def insumosPerdidos(request: Request, fInicio:str='', fFin:str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if fInicio == '':
        fInicio = datetime.datetime.now() - datetime.timedelta(days=30)
        fInicio = fInicio.strftime("%Y-%m-%d")
    if fFin == '':
        fFin = datetime.datetime.now().strftime("%Y-%m-%d")
    data = json_util._json_convert(insumos.perdidosDet(fInicio=fInicio, fFin=fFin))
    return templates.TemplateResponse('insumos_perdidos_det.html', context={'request': request, 'fInicio': fInicio, 'fFin': fFin, 'perdidos': data, 'userInfo': user})

@Reportes.get('/insumos/perdidos_resumen')
async def insumosPerdidos(request: Request, fInicio:str='', fFin:str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if fInicio == '':
        fInicio = datetime.datetime.now() - datetime.timedelta(days=30)
        fInicio = fInicio.strftime("%Y-%m-%d")
    if fFin == '':
        fFin = datetime.datetime.now().strftime("%Y-%m-%d")
    data = json_util._json_convert(insumos.perdidosRes(fInicio=fInicio, fFin=fFin))
    return templates.TemplateResponse('insumos_perdidos_res.html', context={'request': request, 'fInicio': fInicio, 'fFin': fFin, 'perdidos': data, 'userInfo': user})

@Reportes.get('/insumos/utilizados')
async def insumosPerdidos(request: Request, fInicio:str='', fFin:str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if fInicio == '':
        fInicio = datetime.datetime.now() - datetime.timedelta(days=30)
        fInicio = fInicio.strftime("%Y-%m-%d")
    if fFin == '':
        fFin = datetime.datetime.now().strftime("%Y-%m-%d")
    data = json_util._json_convert(insumos.utilizados(fInicio=fInicio, fFin=fFin))
    print(data)
    return templates.TemplateResponse('insumos_utilizados.html', context={'request': request, 'fInicio': fInicio, 'fFin': fFin, 'insumos': data, 'userInfo': user})

@Reportes.get('/insumos/historial_det')
async def historialCompras(request: Request, fInicio:str='', fFin:str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if fInicio == '':
        fInicio = datetime.datetime.now() - datetime.timedelta(days=30)
        fInicio = fInicio.strftime("%Y-%m-%d")
    if fFin == '':
        fFin = datetime.datetime.now().strftime("%Y-%m-%d")
    data = json_util._json_convert(insumos.historialDet(fInicio=fInicio, fFin=fFin))
    print(data)
    return templates.TemplateResponse('historial_compras_det.html', context={'request': request, 'compras': data, 'fInicio': fInicio, 'fFin': fFin, 'userInfo': user})