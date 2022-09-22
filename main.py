#from datetime import datetime
from fastapi import FastAPI, Request, Form
#from fastapi import Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
app = FastAPI()

@app.get("/")
async def form_post(request: Request):
    msg = 'Hola mundo'
    return templates.TemplateResponse('index.html', context={'request': request,'msg': msg})

