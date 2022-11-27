from mongo import filter
from fastapi import HTTPException
from fastapi import status
from jose import jwt, JWTError
from config import settings
from models import tokenUser


class Login():
    def get_user(self, username: str, codTipoUsuario: int):
        return filter("usuarios", {'username': username, "codTipoUsuario": codTipoUsuario})

    async def get_current_user(self, token: str, required_bool: bool = False):
    
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            scheme, _, param = token.partition(" ")
            payload = jwt.decode(
                param, settings.SECRET_KEY, algorithms=settings.ALGORITHM
            )
            #payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            typeUser: int = payload.get("typeUser")
            print(username)
            if username is None:
                if required_bool:
                    return False
                else: raise credentials_exception
        except Exception as e:
            print(e)
            if required_bool:
                return False
            else: raise credentials_exception

        user = self.get_user(username=username, codTipoUsuario= typeUser)
        if user is None:
            if required_bool:
                return False
            else: raise credentials_exception
        userToken = tokenUser(username=username, typeUser=typeUser)
        return userToken

login = Login()
        