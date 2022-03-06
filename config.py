import os
from dotenv import load_dotenv  # Instalar con pip install python-dotenv

load_dotenv()  # Carga todo el contenido de .env en variables de entorno


class Config:
    SERVER_NAME = "localhost:7001"
    DEBUG = True

    DATABASE_PATH = "database\\db_consultas.db"
    DB_TOKEN = os.environ.get("DB_TOKEN", "")  # Para Encriptar la DB
    ENCRYPT_DB = True
    DB_PASSWORD=os.environ.get("DB_PASSWORD","")

