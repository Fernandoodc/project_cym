from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm,  OAuth2PasswordBearer
from utils import OAuth2PasswordBearerWithCookie
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from fastapi.responses import RedirectResponse
from mongo import find, update_one
from bson import json_util, objectid
from mongo import find_one
from models import changePasw
from werkzeug.security import generate_password_hash, check_password_hash
from config import settings
from jose import jwt
from functions import login
from manager import manager, query_user

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")

templates = Jinja2Templates(directory="templates")

Login = APIRouter(tags=['login'])
@Login.get('/login', status_code=status.HTTP_401_UNAUTHORIZED)
async def login(request: Request):
    error = []
    return templates.TemplateResponse('login.html', context={'request': request, 'error': error}, status_code=status.HTTP_401_UNAUTHORIZED)

@Login.post('/login')
async def create_token(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    error = []
    try:
        user = query_user(username)
        if user != None:
            if check_password_hash(user['password'], password):
                access_token = manager.create_access_token(data={'sub': username, 'typeUser': user['codTipoUsuario']})
                response = RedirectResponse('/')
                manager.set_cookie(response=response, token=access_token)
                return response
        error.append('Usuario o Contraseña Incorrecta')
        response.status_code = status.HTTP_401_UNAUTHORIZED
    except Exception as e:
        print(e)
        error.append('Ocurrió un error interno')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return templates.TemplateResponse('login.html', context={'request': request, 'error': error})

@Login.get('/profile')
async def profile(request: Request, user=Depends(manager)):
    usuario = find('usuario', {'username': user.username})
    return templates.TemplateResponse('users-profile.html', context={'request': request, 'usuario': usuario, 'userInfo': user})

@Login.put('/update_passw')
async def actualizarPassword(response: Response, pasw : changePasw, user=Depends(manager)):
    usuario = query_user(user.username)
    if check_password_hash(usuario['password'], pasw.currentPasw):
        hash = generate_password_hash(pasw.newPasw, method=settings.HASH)
        await update_one('usuarios', {'username': user.username}, {'$set': {'password': hash}})
        return {'msg': 'success'}
    response.status_code = status.HTTP_400_BAD_REQUEST
    return {'msg': 'Contraseña incorrecta, intente de nuevo'}

@Login.get('/logout')
async def logout(response: Response, user=Depends(manager)):
    response.delete_cookie(settings.KEY_TOKEN)
    return RedirectResponse('/login')