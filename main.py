import uvicorn
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
from pagos import Pagos
from productos import Productos
from proveedores import Proveedores
from reportes import Reportes
from usuarios import Usuarios
from equipos import Equipos
from functions import login
from jose import jwt
from manager import manager
from mongo import find, find_one, update_one
from config import settings
templates = Jinja2Templates(directory="templates")
app = FastAPI()
client = MongoClient("localhost")
db = client['cym']
#connect(db="cym", host="localhost", port=27017)
app.mount("/static", StaticFiles(directory="assets"), name="static")

app.include_router(Clientes, prefix="/clientes")
app.include_router(Pedidos, prefix="/pedidos")
app.include_router(Trabajos, prefix="/trabajos")
app.include_router(Insumos, prefix="/insumos")
app.include_router(Proveedores, prefix='/proveedores')
app.include_router(Pagos, prefix="/pagos")
app.include_router(Productos, prefix='/productos')
app.include_router(Equipos, prefix='/equipos')
app.include_router(Reportes, prefix='/reportes')
app.include_router(Usuarios, prefix='/usuarios')
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
def agg_user(usuario:models.newUser):
    passw = generate_password_hash(usuario.password, method=settings.HASH)
    data = {
        'username': usuario.username,
        'password': passw
    }
    id = db['usuarios'].insert_one(data)
    print(json_util.dumps(id))



@app.get('/')
async def index(request: Request, user=Depends(manager)):
    return templates.TemplateResponse('index.html', context={'request': request, "userInfo": user})


@app.post('/')
async def index(request: Request, user=Depends(manager)):
    return templates.TemplateResponse('index.html', context={'request': request, "userInfo": user})

@app.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(response : Response ,files: List[UploadFile] = File(...), cod_pedido: str = Form(...), cod_detalle: str = Form(...)):
    if files:
        if(cod_pedido == "" or cod_detalle==""):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'msg': 'Falta codigo de Pedido'}
        path = 'archivos/'+ cod_pedido + '/' + cod_detalle
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
                rutas.append({'ruta': path + '/' + file.filename, 'nombre': file.filename})
        for ruta in rutas:
            db['detallesPedidos'].find_one_and_update({'codPedido': cod_pedido, 'codDetalle': cod_detalle}, {'$push':{'archivos': ruta}})
        return {'msg': 'success', 'path': path, 'files': rutas}
    return 0


@app.post("/upload_diseno", status_code=status.HTTP_200_OK)
async def upload_disenio(response : Response, files: List[UploadFile] = File(...), cod_pedido: str = Form(...), cod_detalle: str = Form(...), cod_produccion: str = Form(...), user=Depends(manager)):
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
#async def upload(response: Response, codPedido:str, codDet: str, filename:str, user=Depends(manager)):
async def upload(response: Response, ruta:str, user=Depends(manager)):
    try:
        #file = open(getcwd() + '/archivos/'+ codPedido + '/' + codDet + "/" + filename)
        file = open(ruta)
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
    #return FileResponse(getcwd() + '/archivos/'+ codPedido + '/' + codDet + "/" + filename)
    return FileResponse(getcwd() + '/'+ ruta)

@app.get("/files/download")
async def upload(response: Response, ruta:str, filename:str = '', user=Depends(manager)):
    try:
        file = open(ruta)
        print(file)
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
    #return FileResponse(getcwd() + '/archivos/'+ codPedido + '/' + codDet + "/" + filename)
    return FileResponse(getcwd() + '/'+ ruta, media_type="application/octet-stream", filename=filename)



@app.get("/get_disenios")
async def getDisenios(response:Response, ruta: str, user=Depends(manager)):
    try:
        file = open(ruta)
        file.close()
    except Exception as e:
        print(e)
        return "Archivo con encontrado"
    return FileResponse(getcwd() + '/'+ ruta)

@app.delete('/delete_archivo')
async def DeleteArchivo(respones: Response, filename: str, cod_pedido: str, cod_detalle: str, user=Depends(manager)):
    path = '/archivos/'+ cod_pedido + '/' + cod_detalle + '/'+ filename
    try:
        remove(getcwd() + path)
        await update_one('detallesPedidos', {'codDetalle': cod_detalle}, {"$pull": {"archivos": {"nombre": filename}}})
        return JSONResponse(content={
            "removed": True
        }, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={
            "removed": False,
            "message": "File not found"
        }, status_code=404)

@app.delete("/delete_disenio")
async def deleteDisenio(response: Response, filename : str, cod_pedido: str, cod_detalle: str, cod_produccion: str, userInfo=Depends(manager)):
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


@app.get('/nacionalidades')
async def nacionalidades():
    try:
        nacs = find_one('nacionalidades')
        print(nacs['_id'])
    except Exception as e:
        print(e)
        return 0
    return json_util._json_convert(nacs)


"""from fastapi import Response, BackgroundTasks
import pdfkit
@app.get("/pdf")
def get_pdf(background_tasks: BackgroundTasks, request:Request):
    options = {
    'page-size': 'a4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    'no-outline': None
}   
    print(str(templates.get_template("login.html")))
    buffer = pdfkit.from_url("www.google.com")
    #buffer = pdfkit.from_file(getcwd()+"/templates/login.html", options=options)

    background_tasks.add_task(buffer)
    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(buffer, headers=headers, media_type='application/pdf')"""

from jinja2 import Environment
from jinja2 import FileSystemLoader
from pdfkit import from_string

from fastapi import Response, BackgroundTasks
from fastapi import Response, BackgroundTasks
@app.get("/pdf")
def create_pdf(background_tasks: BackgroundTasks):
    template_vars = {
        'template_title': 'A template example',
        'template_description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit'
    }

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('pruebas.html')
    html_out = template.render(template_vars, g=1)
    print(html_out)
    file_content = from_string(
        html_out,
        False,
        #options='here_a_dict_with_special_page_properties',
        #css='here_your_css_file_path' # its a list e.g ['my_css.css', 'my_other_css.css']
    )
    #background_tasks.add_task(file_content)
    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(file_content, headers=headers, media_type='application/pdf')
    #return file_content

if __name__ == "__main__":
    uvicorn.run(app,) #host="0.0.0.0", port=8000)