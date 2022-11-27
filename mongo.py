from pymongo import MongoClient, ReturnDocument, errors
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

def find_one(coleccion, condicion={}):
    try:
        reponse = db[coleccion].find_one(condicion)
    except errors.CollectionInvalid as ec:
        print(ec)
        return {}
    except errors.ConnectionFailure as e:
        print(ec)
        return {}
    return reponse

def find(coleccion, condicion={}):
    try:
        reponse = db[coleccion].find(condicion)
    except errors.ConnectionFailure as e:
        print(e)
        return {}
    return reponse

def agreggate(coleccion, condicion):
    response = db[coleccion].aggregate(condicion)
    return response
