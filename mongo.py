from pymongo import MongoClient, ReturnDocument, errors
from pydantic import BaseModel
client = MongoClient("localhost")
db = client['cym']

def filter(coleccion, condicion = {}):
    try:
        data = db[coleccion].find_one(condicion)
        if data == None:
            return None
        return True
    except:
        print("Error de Conección")
        return False

def find_one(coleccion, condicion={}, proyeccion = {}):
    try:
        reponse = db[coleccion].find_one(condicion, proyeccion)
    except Exception as ec:
        print(ec)
        return {}
    return reponse

def find(coleccion, condicion={}):
    try:
        reponse = db[coleccion].find(condicion)
    except Exception as e:
        print(e)
        return {}
    return reponse

def agreggate(coleccion, condicion):
    try:
        response = db[coleccion].aggregate(condicion)
        return response
    except Exception as e:
        print(e)
        return {}

def insert_one(coleccion, contenido):
    try:
        db[coleccion].insert_one(contenido)
    except Exception as e:
        print(e)

async def delete_one(coleccion: str, condicion = {}):
    db[coleccion].delete_one(condicion)

async def delete_many(coleccion: str, condicion = {}):
    db[coleccion].delete_many(condicion)

async def update_one(coleccion: str, condicion = {}, datos = {}):
    db[coleccion].update_one(condicion, datos)

async def find_one_and_update(coleccion : str, condiccion = {}, datos = {}):
    db[coleccion].find_one_and_update(condiccion, {'$set':datos})
