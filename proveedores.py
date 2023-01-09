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
Proveedores = APIRouter()
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
async def agregarFactura(response: Response, factura: facturas):
    filtro = filter('facturasProveedores', {'numeroFactura': factura.numeroFactura})
    if filtro == None:
        insert_one('facturasProveedores', loads(factura.json()))
    elif filtro == True:
        response.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Factura ya existente'}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': 'Error Interno'}