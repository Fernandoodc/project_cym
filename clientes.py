from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from fastapi.responses import RedirectResponse
from config import settings
from functions import login, clientes
from mongo import find, find_one, insert_one, filter, update_one
from bson import json_util, ObjectId
from manager import manager
import models
from json import loads

Clientes = APIRouter()

templates = Jinja2Templates(directory="templates")
@Clientes.get("/clientes", tags=['Clientes'])
def listaClientes(request: Request, id:str='', user=Depends(manager)):
    login.get_current_user(request.cookies.get(settings.KEY_TOKEN))
    clientes = find("clientes")
    #print(json_util.dumps(client))
    response = json_util._json_convert(clientes)
    nacionalidades = json_util._json_convert(find('nacionalidades'))
    return templates.TemplateResponse('clientes.html', context={'request': request, 'clientes': response, 'id': id, 'nacionalidades': nacionalidades, 'userInfo': user})


@Clientes.get("/get_client/", status_code=status.HTTP_200_OK)
async def get_client(response: Response, request: Request, doc, user=Depends(manager)):
    if doc:
        data = find_one('clientes' ,{'documento': doc})
        if(data == None):
            data = find_one('clientes' ,{'_id': ObjectId(doc)})
            if data == None:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {'msg': 'Error'}
        return json_util._json_convert(data)
    response.status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    return {'msg': 'Error'}

@Clientes.get('/deudas')
async def DeudasCliente(response: Response, documento: str, user=Depends(manager)):
    datos = clientes.deudas(documento)
    if datos == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None
    print(datos)
    return json_util._json_convert(datos)

@Clientes.get('/historial_pagos/{_id}')
async def historialPagos(request: Request, _id:str, user=Depends(manager)):
    datos = clientes.pagos(_id)
    print(datos)
    if datos == None:
        return None
    return templates.TemplateResponse('historial_pagos.html', context={'request': request, 'pagos': datos, 'userInfo': user})

@Clientes.get('/historial_pedidos/{_id}')
async def historialPagos(request: Request, _id:str, user=Depends(manager)):
    datos = clientes.pedidos(_id)
    if datos == None:
        return None
    return templates.TemplateResponse('historial_pedidos.html', context={'request': request, 'pedidos': datos, 'userInfo': user})


@Clientes.post("/agg/cliente", status_code=status.HTTP_201_CREATED)
def agg_clientes(cliente: models.clientes, response: Response, user=Depends(manager)):
    filtro = filter('clientes', {'documento': cliente.documento, 'nacionalidades_id': cliente.nacionalidades_id})
    if filtro == None:
        insert_one('clientes', loads(cliente.json()))
        response.status_code = status.HTTP_201_CREATED
        return "success"
    elif filtro == False:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return "Error"
    else:
        response.status_code = status.HTTP_409_CONFLICT
        return "Cliente ya existente"

@Clientes.put('/editar_cliente')
async def editarCliente(response: Response, cliente_id:str ,datos: models.clientes, user=Depends(manager)):
    result = await update_one('clientes', {'_id': ObjectId(cliente_id)}, {'$set': loads(datos.json())})
    print(json_util._json_convert(result))
    return {'msg': 'success'}