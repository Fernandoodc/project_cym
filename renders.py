from http import client
import http
import json
from pydoc import cli
from this import d
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