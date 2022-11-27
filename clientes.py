from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi.responses import RedirectResponse
from config import settings
from functions import login
from mongo import find, find_one
from bson import json_util

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
async def get_client(response: Response, request: Request, doc):
    token = request.cookies.get(settings.KEY_TOKEN)
    user = await login.get_current_user(token=token, required_bool=True)
    if not user:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'msg': "UNAUTHORIZED"}
    if doc:
        data = find_one('clientes' ,{'documento': int(doc)})
        if(data == None):
            response.status_code=status.HTTP_404_NOT_FOUND
            return {'msg': 'Error'}
        return json_util._json_convert(data)
    response.status_code=status.HTTP_404_NOT_FOUND
    return {'msg': 'Error'}
