from fastapi_login import LoginManager
from fastapi import Response
from mongo import find_one
from config import settings
from models import tokenUser
from bson import json_util
from datetime import timedelta
manager = LoginManager( settings.SECRET_KEY, '/login', use_cookie=True, use_header=True, default_expiry=timedelta(hours=8))
@manager.user_loader()
def get_user(username: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    try:
        user = find_one('usuarios', {'username': username}, {'_id': 0,'username': 1, 'codTipoUsuario': 1, 'nombre': 1, 'apellido': 1})
        info = tokenUser(username=user['username'], codTipoUsuario=user['codTipoUsuario'], nombre=user['nombre'], apellido=user['apellido'])
        return info
    except Exception as e:
        print(e, "error")
        return None
    
def query_user(username: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    try:
        return find_one('usuarios', {'username': username}, {'_id': 0,'username': 1, 'password': 1, 'codTipoUsuario': 1})
    except Exception as e:
        print(e)
        return None