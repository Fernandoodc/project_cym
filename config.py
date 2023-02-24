import os
from dotenv import load_dotenv
load_dotenv()


class Settings:
    PROJECT_TITLE: str = "C&M"
    PROJECT_VERSION: str = "0.1"
    MONGODB_USER: str = os.getenv("")
    MONGODB_PASSWORD: str = os.getenv("")
    MONGODB_SERVER: str = os.getenv("MONGODB_SERVER")
    MONGODB_PORT: str = os.getenv("MONGODB_PORT")
    MONGODB_DB: str = os.getenv("MONGODB_DB")
    #DATABASE_URL = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_SERVER}:{MONGODB_PORT}/{MONGODB_DB}"
    MONGODB_URI = f"mongodb://{MONGODB_SERVER}:{MONGODB_PORT}/"  #mongodb://localhost:27017/
    ALGORITHM = "HS256"
    HASH = "pbkdf2:sha256"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    KEY_TOKEN: str = "access-token"
    #IVA
    PORCENTAJE_IVA = 10
    #CANTIDAD DE DIGITOS DE LOS CODIGOS
    COD_INSUMOS = 4
    COD_PRODUCTOS = 4
    NUM_RECIBO = 6
    NUM_FACTURA = 7



settings = Settings()