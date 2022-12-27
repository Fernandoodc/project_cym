from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import Form
from typing import List
from fastapi import UploadFile, File
from fastapi import Depends
from manager import manager
from mongo import find_one, agreggate, update_one, find_one_and_update
from bson import json_util, ObjectId
from datetime import datetime, timedelta
from models import aprovacion
from json import loads
Trabajos = APIRouter()
templates = Jinja2Templates(directory="templates")

@Trabajos.get("/orden_trabajo")
async def pedidos(request: Request):
    """data = agreggate("detallesPedidos", [
        {
            "$lookup":{
                "from": "productos",
                "localField": "detalleProducto.codProducto",
                "foreignField": "codProducto",
                "as": "producto"
            }
        },
        {
            "$unwind": "$producto"
        },
        {
            "$lookup":{
                "from": "produccion",
                "localField": "codDetalle",
                "foreignField": "codDetalle",
                "as": "produccion"
            }
        },
        {
            "$unwind": "$produccion"
        },
        {
            "$project":{
                "codProduccion": "$codDetalle",
                "producto": "$producto.descripcion",
                "cantidadRestante": "$produccion.cantidadRestante",
                "cantidad": "$cantidad",
                "descripcion": "$descripcion",
                "fechaEntrega": "$fechaEntrega",
                "etapa":{
                    "codEtapa": "$produccion.etapa.codEtapa",
                    "descripcion": "$produccion.etapa.descripcion"
                }
                
            }
        }
    ])"""

    ##pasa solo aquellos en que aun no estan terminados o pedidos solicitado hace menos de 30 dias
    hoy = datetime.now()
    mes = hoy - timedelta(days=30)
    data = agreggate("pedidos", [
        {
            "$lookup":{
                "from": "detallesPedidos",
                "localField": "codPedido",
                "foreignField": "codPedido",
                "as": "pedido"
            }
        },
        {
            "$unwind": "$pedido"
        },
        {
            "$lookup":{
                "from": "produccion",
                "localField": "pedido._id",
                "foreignField": "detallesPedidos_id",
                "as": "produccion"
            }
        },
        {
            "$unwind": "$produccion"
        },
        {
            "$lookup":{
                "from": "productos",
                "localField": "pedido.detalleProducto.codProducto",
                "foreignField": "codProducto",
                "as": "producto"
            }
        },
        {
            "$unwind": "$producto"
        },
        {
            "$match":{
                #"$or": [{"fecha": { "$gt": "2022-11-17" }}, {"produccion.etapa.codEtapa": {"$not":{"$eq": 2}}}]
                "$or": [{"fecha": { "$gt": str(mes.date()) }}, {"produccion.etapa.codEtapa": {"$not":{"$eq": 2}}}]
            }
        },
        {
            "$project":{
                "codProduccion": "$produccion.codProduccion",
                "detallePedido_id": "$pedido._id",
                "codPedido": "$codPedido",
                "producto": "$producto.descripcion",
                "cantidadRestante": "$produccion.cantidadRestante",
                "cantidad": "$pedido.cantidad",
                "descripcion": "$descripcion",
                "fechaEntrega": "$pedido.fechaEntrega",
                "etapa":{
                    "codEtapa": "$produccion.etapa.codEtapa",
                    "descripcion": "$produccion.etapa.descripcion"
                }
            }
        }
    ])
    #print(json_util.dumps(data))
    #response = json_util.dumps(data)
    #print(response)
    #print(response['codDetalle'])
    #print(json_util.dumps(data))
    return templates.TemplateResponse("orden_trabajo.html", context={"request": request, 'trabajos': data})

@Trabajos.get("/info_produccion/{cod}")
def infoProduccion(cod: str):
    condition = [
        {"$match": {
            "_id":  ObjectId(cod)
            }
        },
        {
            "$lookup":{
                "from": "productos",
                "localField": "detalleProducto.codProducto",
                "foreignField": "codProducto",
                "as": "producto"
            }
        },
        {
            "$unwind": "$producto"
        },
        {
            "$lookup":{
                "from": "produccion",
                "localField": "_id",
                "foreignField": "detallesPedidos_id",
                "as": "produccion"
            }
        },
        {
            "$unwind": "$produccion"
        },
        {
            "$project":{
                "codProduccion": "$produccion.codProduccion",
                "codPedido": "$codPedido",
                "codDetalle": "$codDetalle",
                "producto": "$producto.descripcion",
                "cantidadRestante": "$produccion.cantidadRestante",
                "cantidad": "$cantidad",
                "descripcion": "$descripcion",
                "fechaEntrega": "$fechaEntrega",
                "etapa":{
                    "codEtapa": "$produccion.etapa.codEtapa",
                    "descripcion": "$produccion.etapa.descripcion"
                },
                "archivos": "$archivos",
                "diseños": "$produccion.diseños",
                "aprovado": "$produccion.aprovado",
                "detalleProducto": "$detalleProducto"
            }
        }
    ]
    data = json_util._json_convert(agreggate("detallesPedidos", condition))
    return data

@Trabajos.post("/upload_disenio")
async def uploadDisenio(response : Response ,files: List[UploadFile] = File(...), cod_pedido: str = Form(...), cod_detalle: str = Form(...)):
    return files

@Trabajos.get("/produccion")
async def produccion(request: Request, user=Depends(manager)):
    return templates.TemplateResponse("produccion.html", context={'request': request, "userInfo": user})

@Trabajos.post("/act_aprovacion")
async def actAprovacion(response: Response, estado: aprovacion):
    #await update_one("produccion", {"codProduccion": estado.codProduccion}, {"aprovado": estado.estado})
    await find_one_and_update("produccion", {"codProduccion": estado.codProduccion}, {"aprovado": estado.estado})
    return "success"
