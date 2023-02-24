from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from bson import json_util, ObjectId
from models import datosUsuario, resetPasw, newUser
from pymongo import MongoClient, errors, ReturnDocument
from werkzeug.security import generate_password_hash
import datetime
import json
from manager import	 manager
from mongo import delete_one, delete_many, find_one, find, update_one
from functions import usuarios
from config import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
Usuarios = APIRouter()

templates = Jinja2Templates(directory="templates")
UPermitidos = [1]

@Usuarios.get('/')
async def listaUsuarios(request: Request, id:str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    users = json_util._json_convert(usuarios.listaUsuarios())
    nacionalidades = db['nacionalidades'].find()
    tiposUsuario = db['tiposUsuarios'].find()
    return templates.TemplateResponse('usuarios.html', context={'request': request, 'usuarios': users, 'nacionalidades': nacionalidades, 'tiposUsuarios': tiposUsuario, 'id':id, 'userInfo': user})

@Usuarios.get('/nuevo_usuario')
async def nuevoUsuario(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    nacionalidades = db['nacionalidades'].find()
    tiposUsuario = db['tiposUsuarios'].find()
    return templates.TemplateResponse('nuevo_usuario.html', context={'request': request, 'nacionalidades': nacionalidades, 'tiposUsuarios': tiposUsuario, 'userInfo': user})
@Usuarios.post('/new_user')
async def agregarUsuario(respose: Response, data:newUser, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if usuarios.verifUsername(newUsername=data.username) != None:
        respose.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Username ya se encuentra en uso'}
    hash = generate_password_hash(data.password, method=settings.HASH)
    data.password = hash
    db['usuarios'].insert_one(json.loads(data.json()))
    return {'msg': 'success'}


@Usuarios.get('/info')
async def infoUser(response: Response, id:str, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    info = json_util._json_convert(usuarios.infoOneUser(id))
    return info

@Usuarios.put('/editar')
async def editarUsuario(respose: Response, id:str, datos:datosUsuario, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    usernameStatus = usuarios.verifUsername(id=id, newUsername=datos.username)
    print(usernameStatus)
    if usernameStatus != None:
        respose.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Username ya se encuentra en uso'}
    db['usuarios'].update_one({'_id': ObjectId(id)}, {'$set': json.loads(datos.json())})
    return {'msg': 'success'}

@Usuarios.get('/verif_username')
async def verificarUsername(respose: Response, username:str, id:str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if usuarios.verifUsername(newUsername=username, id=id) == None:
        return {'msg': 'username disponible'}
    else:
        respose.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'username ya se encuentra en uso'}
    
@Usuarios.put('/change_type_user')
async def cambiaTipoUser(response: Response, idUser:str, newTypeUser:int, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    db['usuarios'].update_one({'_id': ObjectId(idUser)}, {'$set': {'codTipoUsuario': newTypeUser}})
    return {'msg': 'success'}

@Usuarios.put('/reset_password')
async def resetPasword(response: Response, datos:resetPasw, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    paswHash = generate_password_hash(datos.newPassword, method=settings.HASH)
    db['usuarios'].update_one({'_id': ObjectId(datos.userId)}, {'$set': {'password': paswHash}})
    return {'msg': 'success'}

@Usuarios.delete('/eliminar')
async def eliminarUsuario(respose: Response, id:str, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    db['usuarios'].delete_one({'_id': ObjectId(id)})
    return {'msg': 'success'}
