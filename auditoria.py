from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from fastapi import Request, Response
from fastapi import Depends
from models import configuraciones
from pymongo import MongoClient
from bson import json_util
from werkzeug.security import generate_password_hash
from functions import usuarios, Auditorias
import json
from manager import	 manager
from config import settings
auditorias = Auditorias()
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
Auditoria = APIRouter()
templates = Jinja2Templates(directory="templates")
UPermitidos = [1]

@Auditoria.get('/productos')
async def auditProductos(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    data = auditorias.productos()
    return templates.TemplateResponse('auditoria-productos.html', context={'request': request, 'datos': data, 'userInfo': user})

@Auditoria.get('/pedidos')
async def auditPedidos(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    data = auditorias.pedidos()
    return templates.TemplateResponse('auditoria-pedidos.html', context={'request': request, 'datos': data, 'userInfo': user})

@Auditoria.get('/det_pedidos')
async def auditPedidos(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    data = auditorias.detallesPedidos()
    return templates.TemplateResponse('auditoria-det-pedidos.html', context={'request': request, 'datos': data, 'userInfo': user})

@Auditoria.get('/insumos')
async def auditPedidos(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    data = auditorias.insumos()
    return templates.TemplateResponse('auditoria-insumos.html', context={'request': request, 'datos': data, 'userInfo': user})

@Auditoria.get('/proveedores')
async def auditPedidos(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    data = auditorias.proveedores()
    return templates.TemplateResponse('auditoria-proveedores.html', context={'request': request, 'datos': data, 'userInfo': user})