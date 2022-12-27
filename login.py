from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm,  OAuth2PasswordBearer
from utils import OAuth2PasswordBearerWithCookie
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from fastapi.responses import RedirectResponse
from mongo import find, find_one, agreggate
from bson import json_util, objectid
from mongo import find_one
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

"""""
@Login.get("/")
async def form_login(request: Request):
    token = request.cookies.get("access_token")
    validation = await login.get_current_user(token=token, required_bool=True)
    if validation:
         return RedirectResponse("/index")
    error = []
    return templates.TemplateResponse('login.html', context={'request': request,'error': error})

@Login.post("/")
def retrieve_token_for_authenticated_user(request:Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    error = []
    try:
        if form_data.username and form_data.password:
            user = find_one('usuarios', {'username': form_data.username})
            if user != None:
                print(user['username'])
                if check_password_hash(user['password'], form_data.password):
                    data = {"sub": form_data.username, "typeUser": user['codTipoUsuario']}
                    jwt_token = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
                    response = RedirectResponse("/index")
                    response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
                    return response
            error.append('Usuario o Contraseña Incorrecta')
            response.status_code = status.HTTP_401_UNAUTHORIZED
    except:
        error.append("Ocurrió un Error Interno")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return templates.TemplateResponse('login.html', context={'request': request, 'error': error})
"""