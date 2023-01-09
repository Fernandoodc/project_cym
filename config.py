import os
from dotenv import load_dotenv
os.getenv(".env")
load_dotenv(dotenv_path=".env")


class Settings:
    PROJECT_TITLE: str = "C&M"
    PROJECT_VERSION: str = "0.1"
    MONGODB_USER: str = os.getenv("")
    MONGODB_PASSWORD: str = os.getenv("")
    MONGODB_SERVER: str = os.getenv("MONGODB_SERVER", "localhost")
    MONGODB_PORT: str = os.getenv("MONGODB_PORT", 5432)
    MONGODB_DB: str = os.getenv("MONGODB_DB", "db_jobcard")
    #DATABASE_URL = f"MONGODBql://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_SERVER}:{MONGODB_PORT}/{MONGODB_DB}"
    ALGORITHM = "HS256"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    KEY_TOKEN: str = "access_token"
    #CANTIDAD DE DIGITOS DE LOS CODIGOS
    COD_INSUMOS = 4


settings = Settings()