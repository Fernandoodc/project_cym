from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import Form
from fastapi import status
from fastapi import Depends
from manager import manager
from mongo import insert_one, filter, find
from bson import json_util, ObjectId
from datetime import datetime, timedelta
from models import proveedores, facturas
from json import loads
from config import settings
from pymongo import MongoClient
Proveedores = APIRouter()
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
templates = Jinja2Templates(directory="templates")

@Proveedores.post('/agregar_proveedor', status_code=status.HTTP_201_CREATED)
async def agregarProveedor(response: Response, proveedor: proveedores, user = Depends(manager)):
    data = {
        '_id': proveedor.ruc,
        'nombre': proveedor.nombre,
        'direccion': proveedor.direccion,
        'celular': proveedor.celular,
        'email': proveedor.email
    }
    print(data)
    filtro = filter('proveedores', {'_id': proveedor.ruc})
    if filtro == None:
        insert_one('proveedores', data)
        return {'msg': 'Proveedor Agregador'}
    elif filtro == True:
        response.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Proveedor ya Existente'}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': 'Error Interno'}
    
@Proveedores.get('/{ruc}/facturas')
async def obtenerFacturas(response: Response, ruc: str, user = Depends(manager)):
    facturas = find('facturasProveedores', {'Proveedores_id': ruc})
    return json_util._json_convert(facturas)

@Proveedores.post('/facturas/agregar_factura')
async def agregarFactura(response: Response, factura: facturas, user=Depends(manager)):
    print(factura)
    filtro = filter('facturasProveedores', {'numeroFactura': factura.numeroFactura, 'Proveedores_id': factura.Proveedores_id})
    if filtro == None:
        insert_one('facturasProveedores', loads(factura.json()))
    elif filtro == True:
        response.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Factura ya existente'}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': 'Error Interno'}

@Proveedores.get('/')
async def listaProveedores(request:Request, ruc:str='', user=Depends(manager)):
    datos = db['proveedores'].find()
    return templates.TemplateResponse('proveedores.html', context={'request': request, 'proveedores': datos, 'ruc': ruc, 'userInfo': user})

@Proveedores.get('/proveedor')
async def infoProveedor(response: Response, ruc:str, user=Depends(manager)):
    return json_util._json_convert(db['proveedores'].find_one({'_id': ruc}))

@Proveedores.post('/proveedor/editar')
async def actulizarProveedor(response: Response, datos: proveedores, user=Depends(manager)):
    if filter('proveedores', {'_id': datos.ruc}) == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': 'Proveedor no encontrado'}
    datos = {
        '_id': datos.ruc,
        'nombre': datos.nombre,
        'direccion': datos.direccion,
        'celular': datos.celular,
        'email': datos.email
    }
    anterior = db['proveedores'].find_one({'_id': datos['_id']})
    usuario_id = db['usuarios'].find_one({'username': user.username})
    auditoria = {
        'usuario': usuario_id['_id'],
        'fecha': datetime.now().strftime("%Y-%m-%d"),
        'accion': 'editar',
        'ruc': datos.ruc,
        'anterior': json_util._json_convert(anterior),
        'cambios': datos
    }
    db['auditoriaProveedores'].insert_one(auditoria)
    db['proveedores'].update_one({'_id': datos['_id']}, {'$set': datos})
    return {'msg': 'success'}