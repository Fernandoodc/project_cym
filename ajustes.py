from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import Depends
from models import configuraciones
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from functions import usuarios
import json
from manager import	 manager
from config import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
Ajustes = APIRouter()
templates = Jinja2Templates(directory="templates")
UPermitidos = [1]

@Ajustes.get('/')
async def ajustes(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    datos = db['configuraciones'].find_one()
    return templates.TemplateResponse('ajustes.html', context={'request': request, 'ajustes': datos, 'userInfo': user})

@Ajustes.put('/actualizar')
async def actualizarAjustes(response: Response, datos: configuraciones, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    db['configuraciones'].update_many({}, {'$set': json.loads(datos.json())})
    return {'msg': 'success'}