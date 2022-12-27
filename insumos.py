from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from mongo import find, find_one
from bson import json_util
from manager import manager

Insumos = APIRouter()
templates = Jinja2Templates(directory="templates")

@Insumos.get("/insumos")
async def listaInsumos(request: Request, user=Depends(manager)):
    data = find("insumos")
    return templates.TemplateResponse("insumos.html", context={'request': request, 'insumos': data, 'userInfo': user})

@Insumos.get("/nuevo_insumo")
async def nuevoInsumo(request: Request):
    return templates.TemplateResponse("nuevo_insumo.html", context={'request': request})

@Insumos.get("/compra_insumos")
async def listaInsumos(request: Request, user=Depends(manager)):
    data = find("insumos")
    return templates.TemplateResponse("compras_de_insumos.html", context={'request': request, 'insumos': data, 'userInfo': user})