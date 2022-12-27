import pathlib
import json
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Response, status
from fastapi import FastAPI
from fastapi import Path
from fastapi import Form
from fastapi import Depends
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson import json_util, ObjectId
import models
import datetime
from os import getcwd, mkdir, makedirs, remove
from mongoengine import connect
from pymongo import MongoClient, ReturnDocument, errors
from werkzeug.security import generate_password_hash, check_password_hash
from clientes import Clientes
from pedidos import Pedidos
from trabajos import Trabajos
from insumos import Insumos
from login import Login
from functions import login
from jose import jwt
from manager import manager
from mongo import find, find_one, update_one
templates = Jinja2Templates(directory="templates")
app = FastAPI()
client = MongoClient("localhost")
db = client['cym']
connect(db="cym", host="localhost", port=27017)
app.mount("/static", StaticFiles(directory="assets"), name="static")

app.include_router(Clientes, prefix="/clientes")
app.include_router(Pedidos, prefix="/pedidos")
app.include_router(Trabajos, prefix="/trabajos")
app.include_router(Insumos, prefix="/insumos")
app.include_router(Login)

@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def ERROR_404(request: Request, _):
    return templates.TemplateResponse("pages-error-404.html", context={"request": request},status_code=404)

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def UNAUTHORIZED_401(request: Request, _):
    return RedirectResponse("/login")
    


@app.get('/get_users')
def get_users():
    users = db['usuarios'].find()
    response = json_util._json_convert(users)
    return response

@app.get('/get_user/{}')
def get_users(id):
    user = db['usuarios'].find({'_id': ObjectId(id)})
    response = json_util._json_convert(user)
    return response

@app.post('/agg/user/')
def agg_user(usuario:models.user):
    passw = generate_password_hash(usuario.password, method='pbkdf2:sha256')
    data = {
        'username': usuario.username,
        'password': passw
    }
    id = db['usuarios'].insert_one(data)
    print(json_util.dumps(id))

#---------Productos---------

@app.post("/agg/product", status_code=status.HTTP_201_CREATED)
async def agg_product(product: models.product):
    data = json.loads(product.json())
    #for i in range(len(data['variaciones']['insumosPorVariacion'])):
    for i in range(len(data['insumos'])):
        #falta comprovación de si existe ese insumo en la bd
            #data['variaciones']['insumosPorVariacion'][i]['insumo_id'] = {
             #   "$oid": data['variaciones']['insumosPorVariacion'][i]['insumo_id']
            #}
        #falta ordenar los descuentos con burbuja, para evitar errores en el js
            aux = data['insumos'][i]['insumo_Id']
            data['insumos'][i]['insumo_Id'] = ObjectId(aux)
    print(db['productos'].insert_one(data))

@app.get("/get-products")
async def get_products():
    productos= db['productos'].find()
    return json_util._json_convert(productos)



@app.get('/')
async def index(request: Request, user=Depends(manager)):
    return templates.TemplateResponse('index.html', context={'request': request, "userInfo": user})
   
@app.post('/')
async def index(request: Request, user=Depends):
    return templates.TemplateResponse('index.html', context={'request': request, "userInfo": user})



#pedidos ---------------------

#no se usa por el momento
@app.post('/agg_pedido', status_code=status.HTTP_201_CREATED)
async def agg_pedido(pedido: models.pedidos, response: Response):
    if(pedido.cliente_id==""):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'msg': 'error'}
    date = datetime.datetime.now().strftime("%y%m")
    seq = db['seq'].find_one_and_update({"date": date}, {"$inc":{"seq": 1}}, upsert = True, return_document=ReturnDocument.AFTER)
    resp = db['pedidos'].insert_one({
        "codPedido": "PE"+str(date)+str(seq['seq']),
        "fecha": pedido.fecha,
        "subTotal": pedido.subtotal,
        "descuento": pedido.descuento,
        "presupuesto": pedido.presupuesto,
        "cliente_id": ObjectId(pedido.cliente_id)      
    })
    return {'codPedido', resp.CodPedido}                

#@app.post('/sum_presu_pedido') #sumar nuevo valores al presupuesto y el subtotal del pedido



@app.get("/pruebas")
async def pruebas(request: Request, response: Response):
    response.set_cookie(key="gg", value="ff")
    
    return templates.TemplateResponse("pruebas.html", context={"request": request, "msg": "hola"})

@app.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(response : Response ,files: List[UploadFile] = File(...), cod_pedido: str = Form(...), cod_detalle: str = Form(...)):
    if files:
        if(cod_pedido == "" or cod_detalle==""):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'msg': 'Falta codigo de Pedido'}
        print(cod_pedido)
        path = 'archivos/'+ cod_pedido + '/' + cod_detalle
        #path = pathlib.Path('/archivos/'+cod_pedido)
        #path.mkdir(parents=False)
        makedirs(path, exist_ok=True)
        print(cod_pedido)
        rutas = []
        for file in files:
            print(file)
            with open(getcwd() + '/'+ path + '/' + file.filename, "wb") as myfile:
            #with open(getcwd() + "/archivos/" + file.filename, "wb") as myfile:
                content = await file.read()
                myfile.write(content)
                myfile.close()
                rutas.append({'ruta': path + '/' + file.filename, 'nombre': file.filename})
        db['detallesPedidos'].find_one_and_update({'codPedido': cod_pedido, 'codDetalle': cod_detalle}, {'$set':{'archivos': rutas}})
        return {'msg': 'success', 'path': path, 'files': rutas}
    return 0

@app.post("/upload_diseno", status_code=status.HTTP_200_OK)
async def upload_disenio(response : Response, files: List[UploadFile] = File(...), cod_pedido: str = Form(...), cod_detalle: str = Form(...), cod_produccion: str = Form(...)):
    if files:
        if(cod_pedido == "" or cod_detalle==""):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'msg': 'Falta codigo de Pedido'}
        path = 'archivos/'+ cod_pedido + '/' + cod_detalle + '/diseños'
        #path = pathlib.Path('/archivos/'+cod_pedido)
        #path.mkdir(parents=False)
        makedirs(path, exist_ok=True)
        rutas = []
        for file in files:
            print(file)
            with open(getcwd() + '/'+ path + '/' + file.filename, "wb") as myfile:
            #with open(getcwd() + "/archivos/" + file.filename, "wb") as myfile:
                content = await file.read()
                myfile.write(content)
                myfile.close()
                rutas.append({'ruta': path + '/' + file.filename, 'descripcion': file.filename})
        #db['produccion'].find_one_and_update({'codProduccion': cod_produccion}, {'$set':{ "$push": {'diseños': rutas}}})
        for ruta in rutas:
            db['produccion'].update_one({'codProduccion': cod_produccion}, {"$push": {"diseños": ruta}})
        return {'msg': 'success', 'path': path, 'files': rutas}
    return 0

@app.get("/files")
async def upload(response: Response, codPedido:str, codDet: str, filename:str, user=Depends(manager)):
    try:
        file = open(getcwd() + '/archivos/'+ codPedido + '/' + codDet + "/" + filename)
        file.close()
    except RuntimeError as e:
        fResponse = 0
        file = {}
        return "Archivo no encontrado"
    except FileExistsError as nf:
        fResponse = 0
        print(nf)
        return "Archivo no encontrado"
    except FileNotFoundError as nf:
        fResponse = 0
        return "Archivo no encontrado"
        #return 0
    return FileResponse(getcwd() + '/archivos/'+ codPedido + '/' + codDet + "/" + filename)

@app.get("/get_disenios")
async def getDisenios(response:Response, ruta: str, user=Depends(manager)):
    try:
        file = open(ruta)
        file.close()
    except Exception as e:
        print(e)
        return "Archivo con encontrado"
    return FileResponse(getcwd() + '/'+ ruta)

@app.get('/nacionalidades')
async def nacionalidades():
    try:
        nacs = find_one('nacionalidades')
        print(nacs['_id'])
    except Exception as e:
        print(e)
        return 0
    return json_util._json_convert(nacs)

@app.delete("/delete_disenio")
async def deleteDisenio(response: Response, filename : str, cod_pedido: str, cod_detalle: str, cod_produccion: str):
    path = '/archivos/'+ cod_pedido + '/' + cod_detalle + '/diseños/'+ filename
    try:
        remove(getcwd() + path)
        await update_one('produccion', {'codProduccion': cod_produccion}, {"$pull": {"diseños": {"descripcion": filename}}})
        return JSONResponse(content={
            "removed": True
        }, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={
            "removed": False,
            "message": "File not found"
        }, status_code=404)
