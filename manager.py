from fastapi_login import LoginManager
from fastapi import Response
from mongo import find_one
from config import settings
from models import tokenUser
from datetime import timedelta
manager = LoginManager( settings.SECRET_KEY, '/login', use_cookie=True, use_header=False, default_expiry=timedelta(hours=8))

@manager.user_loader()
def get_user(username: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    try:
       
        user = find_one('usuarios', {'username': username}, {'_id': 0,'username': 1, 'codTipoUsuario': 1})
        info = tokenUser(username=user['username'], typeUser=user['codTipoUsuario'])
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
