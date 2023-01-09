from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from config import settings
from mongo import find, find_one_and_update, insert_one, filter
from pymongo import ReturnDocument, MongoClient
from bson import json_util, ObjectId
from manager import manager
import json
from models import insumo, compraInsumo
client = MongoClient("localhost")
db = client[settings.MONGODB_DB]

Insumos = APIRouter()
templates = Jinja2Templates(directory="templates")

@Insumos.get("/insumos")
async def listaInsumos(request: Request, user=Depends(manager)):
    data = find("insumos")
    return templates.TemplateResponse("insumos.html", context={'request': request, 'insumos': data, 'userInfo': user})

@Insumos.get("/nuevo_insumo")
async def nuevoInsumo(request: Request):
    return templates.TemplateResponse("nuevo_insumo.html", context={'request': request})

@Insumos.post("/nuevo_insumo", status_code=status.HTTP_201_CREATED)
async def agregarInsumor(response: Response, insumo: insumo):
    seq = db['seq'].find_one_and_update({"cod": 1}, {"$inc":{"seq": 1}}, upsert=True , return_document=ReturnDocument.AFTER)
    cod = '0'*(settings.COD_INSUMOS - len(str(seq['seq']))) + str(seq["seq"])
    print(cod)
    if filter('insumos', {'codInsumo': cod}):
        response.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Error interno de codificacion'}
    #datos = json.loads(insumo.json())
    datos = json.loads(insumo.json())
    print(datos)
    datos['codInsumo'] = cod
    insert_one('insumos', datos)
    return cod

@Insumos.get("/compra_insumos")
async def listaInsumos(request: Request, user=Depends(manager)):
    insumos = find("insumos")
    tiposInsumos = find("tiposInsumos")
    proveedores = find("proveedores")
    return templates.TemplateResponse("compras_de_insumos.html", context={'request': request, 'insumos': insumos,'proveedores': proveedores , 'tiposInsumos': tiposInsumos ,'userInfo': user})

@Insumos.post("/compra_insumos", status_code=status.HTTP_201_CREATED)
async def registrarCompra(response:Response, detalle : compraInsumo):
    id = db['comprasInsumos'].insert_one(json.loads(detalle.json()))
    db['insumos'].update_one({'codInsumo': detalle.codInsumo}, {"$inc": {"stock": detalle.cantidad} })
    return str(id.inserted_id)

@Insumos.delete("/compra_insumos/eliminar_compra", status_code=status.HTTP_200_OK)
async def eliminarCompra(response: Response, idCompra:str):
    compra = json_util._json_convert(db['comprasInsumos'].find_one({'_id': ObjectId(idCompra)}))
    insumo = json_util._json_convert(db['insumos'].find_one({"codInsumo": compra['codInsumo']}))
    if (insumo['stock']- compra['cantidad']<0):
        response.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'No compra no puede ser eliminada'}
    db['comprasInsumos'].delete_one({'_id': ObjectId(idCompra)})
    db['insumos'].update_one({"codInsumo": compra['codInsumo']}, {"$inc": {"stock": -compra['cantidad']} })
    return {'msg': 'success'}


