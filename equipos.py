from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import Form, status
from typing import List
from fastapi import UploadFile, File
from fastapi import Depends
from fastapi.responses import RedirectResponse
from manager import manager
from mongo import find, filter
from bson import json_util, ObjectId
from datetime import datetime, timedelta
from models import equipo, registroMantenimiento
from json import loads
from config import settings
from pymongo import ReturnDocument, MongoClient
from functions import equipos, usuarios
Equipos = APIRouter()
templates = Jinja2Templates(directory="templates")
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]

UPermitidos = [1]

@Equipos.get('/equipos')
async def listaEquipos(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    datos = json_util._json_convert(equipos.datosEquipos())
    return templates.TemplateResponse('equipos.html', context={'request': request, 'equipos': datos, 'userInfo': user})

@Equipos.get('/datos')
async def datosEquipo(response: Response, id:str, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    datos = json_util._json_convert(equipos.datoEquipo(id))
    return datos

@Equipos.get('/nuevo_equipo')
async def nuevoEquipo(request: Request, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    marcas = json_util._json_convert(find('marcasEquipos', {}))
    tiposEquipos = json_util._json_convert(find('tiposEquipos', {}))
    return templates.TemplateResponse('nuevo_equipo.html', context={'request': request,'marcas': marcas, 'tiposEquipos': tiposEquipos, 'userInfo': user})

@Equipos.post('/agregar_equipo')
async def agregarEquipo(response: Response, datos:equipo, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if(datos.tipoEquipo.tipo_id == 'other' and (datos.tipoEquipo.descripcion == '' or datos.tipoEquipo.descripcion == None )) or (datos.marcaEquipo.marca_id == 'other' and (datos.marcaEquipo.descripcion == '' or  datos.marcaEquipo.descripcion == None)):
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {'msg': 'Tipo de equipo o marca no válida'}
    
    if(datos.tipoEquipo.tipo_id == 'other'):
        tipo_id = db['tiposEquipos'].insert_one({'descripcion': datos.tipoEquipo.descripcion})
        tipo_id = tipo_id.inserted_id
    else:
        tipo_id = ObjectId(datos.tipoEquipo.tipo_id)

    if(datos.marcaEquipo.marca_id == 'other'):
        marca_id = db['marcasEquipos'].insert_one({'descripcion': datos.marcaEquipo.descripcion}).inserted_id
    else:
        marca_id = ObjectId(datos.marcaEquipo.marca_id)
    datosEquipo = {
        'numSerie': datos.numSerie,
        'modelo': datos.modelo,
        'fechaAdquisicion': datos.fechaAdquisicion,
        'Tipos_Equipos_id': tipo_id,
        'Marcas_Equipos_id': marca_id
    }
    db['equipos'].insert_one(datosEquipo)
    return {'msg': 'success'}

@Equipos.post('/eliminar_equipo')
async def eliminarEquipo(response: Response, id:str , user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    db['equipos'].delete_one({'_id': ObjectId(id)})
    return {'msg': 'success'}

@Equipos.get('/agregar_matenimiento/{id}')
async def nuevoManteniento(request: Request, id:str, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    datos = json_util._json_convert(equipos.datoEquipo(id))
    tiposMantenimiento = json_util._json_convert(db['tiposMantenimiento'].find())
    return templates.TemplateResponse('nuevo_mantenimiento.html', context={'request': request, 'equipo': datos, 'tiposMatenimiento': tiposMantenimiento, 'userInfo': user})

@Equipos.post('/agregar_mantenimiento')
async def agregarMantenimiento(respose: Response, datos: registroMantenimiento, user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if datos.tipoMantenimiento.tipo_id == 'other' and (datos.tipoMantenimiento.descripcion == None or datos.tipoMantenimiento.descripcion == ''):
        respose.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {'msg': 'Tipo de mantenimiento no válido'}
    
    if datos.tipoMantenimiento.tipo_id == 'other':
        tipo_id =  db['tiposMantenimiento'].insert_one({'descripcion': datos.tipoMantenimiento.descripcion}).inserted_id
    else:
        tipo_id = ObjectId(datos.tipoMantenimiento.tipo_id)
        if filter('tiposMantenimiento', {'_id': tipo_id}) == None:
            respose.status_code = status.HTTP_400_BAD_REQUEST
            return {'msg': 'id de matenimineto no valido'}
    datosMatenimiento = {
        'fecha': datos.fecha,
        'descripcion': datos.descripcion,
        'Tipos_Mantenimiento_id': tipo_id
    }
    print(datos)
    print(datosMatenimiento)
    db['equipos'].update_one({'_id': ObjectId(datos.idEquipo)}, {'$push': {'Mantenimientos': datosMatenimiento}})
    return {'msg', 'success'}

@Equipos.get('/mantenimientos')
async def mantenimientos(request: Request, id : str='', user=Depends(manager)):
    usuarios.controlAcceso(UPermitidos, user)
    if id=='':
        datos = json_util._json_convert(equipos.mantenimientos())
    else:
        datos = [json_util._json_convert(equipos.mantenimientosOneEquipo(id))]
    return templates.TemplateResponse('mantenimientos.html', context={'request': request, 'equipos': datos, 'userInfo': user})