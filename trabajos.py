from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import Form
from typing import List
from fastapi import UploadFile, File
from mongo import find_one, agreggate
from bson import json_util
Trabajos = APIRouter()
templates = Jinja2Templates(directory="templates")

@Trabajos.get("/orden_trabajo")
async def pedidos(request: Request):
    data = agreggate("detallesPedidos", [
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
    ])
    #response = json_util.dumps(data)
    #print(response)
    #print(response['codDetalle'])
    #print(json_util.dumps(data))
    return templates.TemplateResponse("orden_trabajo.html", context={"request": request, 'trabajos': data})


@Trabajos.get("/info_produccion/{cod}")
def infoProduccion(cod: str):
    condition = [
        {"$match": {
            "codDetalle": cod
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
                "codPedido": "$codPedido",
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
                "diseños": "$produccion.diseños"
            }
        }
    ]
    data = json_util._json_convert(agreggate("detallesPedidos", condition))
    return data

@Trabajos.post("/upload_disenio")
async def uploadDisenio(response : Response ,files: List[UploadFile] = File(...), cod_pedido: str = Form(...), cod_detalle: str = Form(...)):
    return files