from fastapi_login import LoginManager
from mongo import find_one
from config import settings
manager = LoginManager(settings.SECRET_KEY, '/login', use_cookie=True, use_header=False)

"""""
DB = {
    'users': {
        'John Doe': {
            'name': 'John Doe',
            'password': 'hunter2',
            'permitions': [1,2]
        }
    }
}
"""
@manager.user_loader()
def query_user(username: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    try:
        return find_one('usuarios', {'username': username})
    except Exception as e:
        print(e)
        return None
