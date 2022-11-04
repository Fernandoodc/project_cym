
import json
from urllib import response
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Response, status
from fastapi import FastAPI
from fastapi import Path
from fastapi import Form
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bson import json_util, ObjectId
import models
from mongoengine import connect
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
templates = Jinja2Templates(directory="templates")
app = FastAPI()
client = MongoClient("localhost")
db = client['cym']
connect(db="cym", host="localhost", port=27017)

app.mount("/static", StaticFiles(directory="assets"), name="static")

@app.get("/")
async def form_login(request: Request):
    msg = 'Hola mundo'
    return templates.TemplateResponse('login.html', context={'request': request,'msg': msg})

@app.post('/login/', status_code=status.HTTP_202_ACCEPTED)
async def form_login(usuario:models.user, response: Response):
    print(usuario)
    if usuario.username and usuario.password:
        filtro = models.Usuarios.objects().filter(username=usuario.username)
        if filtro:
            datos = models.Usuarios.objects().get(username=usuario.username)
            #if datos.username==user and datos.password== passw:
            if datos.username==usuario.username and check_password_hash(datos.password, usuario.password):
                response.status_code = status.HTTP_202_ACCEPTED
                return {'msg': 'ok'}
    #return templates.TemplateResponse('login.html', context={'request': request})
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {'msg': 'rechazado'}

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

@app.post("/agg/clients")
def agg_clientes(cliente: models.clientes):
    db['clientes'].insert_one(json.loads(cliente.json()))
    

@app.get('/index')
async def index(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

#clientes -----------------
@app.get('/clientes')
async def clientes(request: Request):
    clientes = db['clientes'].find()
    #print(json_util.dumps(client))
    response = json_util._json_convert(clientes)
    return templates.TemplateResponse('cym_clientes.html', context={'request': request, 'clientes': response})

@app.get("/get_client/", status_code=status.HTTP_200_OK)
async def get_client(response: Response, doc):
    data = db['clientes'].find_one({'documento': int(doc)})
    if(data == None):
        response.status_code=status.HTTP_404_NOT_FOUND
    return json_util._json_convert(data)

#pedidos ---------------------
@app.get('/nuevo_pedido')
async def nuevo_pedido(request: Request):
    productos =json_util._json_convert(db['productos'].find())
    #print(json_util.dumps(productos))
    delivery = json_util._json_convert(db['delivery'].find_one())
    return templates.TemplateResponse('cym_nuevo_pedido.html', context={'request': request, 'productos': productos, 'delivery' : delivery})    

@app.get("/pruebas")
async def pruebas():
    data = {
    "cod_produto": "PR00004",
    "descripcion": "Impresion Documentos B&N",
    "precio_base": 500,
    "descuentos": {
        "cantidad": 50,
        "descuento": 400
    },
    "variaciones": {
        "codVariacion": "BA001",
        "descripcion": "Standard",
        "precio_extra": 0,
        "insumosPorVariacion": [
        {
            "insumo_id": ObjectId('6354bd72db9719097be374fa'),
            "cantidad": 0
        }
        ]
    },
    "metodoCalculo": {
        "codMetodo": 1,
        "descripcion": "Cantidad"
    }
    }
    db['productos'].insert_one(data)
    return 'ok'

