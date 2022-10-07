from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi import FastAPI
from fastapi import Path
from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Usuarios
from mongoengine import connect
templates = Jinja2Templates(directory="templates")
app = FastAPI()
connect(db="cym", host="localhost", port=27017)

app.mount("/static", StaticFiles(directory="assets"), name="static")
@app.get("/")
async def form_login(request: Request):
    msg = 'Hola mundo'
    return templates.TemplateResponse('login.html', context={'request': request,'msg': msg})
@app.post('/')
async def form_login(request: Request, user : str = Form(...), passw : str = Form(...)):
    if user and passw:
        filtro = Usuarios.objects().filter(username=user)
        if filtro:
            datos = Usuarios.objects().get(username=user)
            if datos.username==user and datos.password== passw:
                return templates.TemplateResponse('index.html', context={'request': request})
    return templates.TemplateResponse('login.html', context={'request': request})

@app.get('/index')
async def index(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})



