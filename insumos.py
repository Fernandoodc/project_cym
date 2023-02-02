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
from models import insumo, compraInsumo, bajaInsumo
from functions import insumos
client = MongoClient(settings.MONGODB_SERVER)
db = client[settings.MONGODB_DB]

Insumos = APIRouter()
templates = Jinja2Templates(directory="templates")

@Insumos.get("/insumos")
async def listaInsumos(request: Request, user=Depends(manager)):
    data = json_util._json_convert(insumos.infoAllInsumos())
    return templates.TemplateResponse("insumos.html", context={'request': request, 'insumos': data, 'userInfo': user})

@Insumos.get('/baja_insumos')
async def formBajaInsumos(request: Request, user=Depends(manager)):
    data = json_util._json_convert(insumos.infoAllInsumos())
    motivos = json_util._json_convert(db['motivosBaja'].find())
    return templates.TemplateResponse('baja_insumos.html', context={'request': request, 'insumos': data, 'motivos': motivos, 'userInfo': user})

@Insumos.post('/baja_insumos')
async def bajaInsumos(respose: Response, datos: bajaInsumo, user=Depends(manager)):
    if(datos.cantidad < 0):
        respose.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {'msg', 'La cantidad no puede ser negativa'}
    if(datos.motivo.motivo_id == 'other'):
        if datos.motivo.descripcion == '':
            respose.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {'msg': 'Se requiere un motivo de baja'}
        motivo_id = db['motivosBaja'].insert_one({'descripcion': datos.motivo.descripcion})
        motivo_id = motivo_id.inserted_id
    else: 
        if db['motivosBaja'].find_one({'_id': ObjectId(datos.motivo.motivo_id)}) == None:
            respose.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {'msg': 'motivo_id inválido'}
        motivo_id = ObjectId(datos.motivo.motivo_id)
    userId = db['usuarios'].find_one({'username': user.username})['_id']
    infoBaja = {
        'codInsumo': datos.codInsumo,
        'cantidad': datos.cantidad,
        'fecha': datos.fecha,
        'motivosBajas_id': motivo_id,
        'usuarios_id': userId
    }
    db['bajasDeInsumos'].insert_one(infoBaja)

    result = db['insumos'].find_one_and_update(filter={'codInsumo': datos.codInsumo}, update={'$inc': {'stock': -datos.cantidad}}, return_document=ReturnDocument.AFTER)
    if result['stock'] < 0:
        db['insumos'].update_one({'codInsumo': datos.codInsumo}, {'$inc': {'stock': datos.cantidad}})
        respose.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {'msg', 'La cantidad inválido'}
    return {'msg': 'success'}

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

@Insumos.get("/infoInsumo")
async def infoInsumo(response: Response, codInsumo: str):
    insumo = db['insumos'].find_one({'codInsumo': codInsumo})
    return json_util._json_convert(insumo)