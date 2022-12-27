from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from fastapi.responses import RedirectResponse
from config import settings
from functions import login
from mongo import find, find_one, insert_one, filter
from bson import json_util
from manager import manager
import models
from json import loads

Clientes = APIRouter()

templates = Jinja2Templates(directory="templates")
@Clientes.get("/clientes", tags=['Clientes'])
def clientes(request: Request):
    login.get_current_user(request.cookies.get(settings.KEY_TOKEN))
    clientes = find("clientes")
    #print(json_util.dumps(client))
    response = json_util._json_convert(clientes)
    return templates.TemplateResponse('cym_clientes.html', context={'request': request, 'clientes': response})


@Clientes.get("/get_client/", status_code=status.HTTP_200_OK)
async def get_client(response: Response, request: Request, doc, user=Depends(manager)):
    """""
    token = request.cookies.get(settings.KEY_TOKEN)
    user = await login.get_current_user(token=token, required_bool=True)
    if not user:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'msg': "UNAUTHORIZED"}
    """
    if doc:
        data = find_one('clientes' ,{'documento': doc})
        if(data == None):
            response.status_code=status.HTTP_404_NOT_FOUND
            return {'msg': 'Error'}
        return json_util._json_convert(data)
    response.status_code=status.HTTP_404_NOT_FOUND
    return {'msg': 'Error'}

@Clientes.post("/agg/cliente", status_code=status.HTTP_201_CREATED)
def agg_clientes(cliente: models.clientes, response: Response):
    filtro = filter('clientes', {'documento': cliente.documento, 'nacionalidad': cliente.nacionalidad})
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
    