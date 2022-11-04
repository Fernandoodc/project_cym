from bson import ObjectId
from turtle import st
from typing import List
from mongoengine import Document, StringField
from pydantic import BaseModel

class Usuarios(Document):
    username = StringField()
    password = StringField()

class user(BaseModel):
    username: str
    password: str

class clientes(BaseModel):
    documento: int
    nombre: str
    apellido: str
    email: str
    celular: str
    direccion: str
    saldo: int = 0

#productos
class pMaroristas(BaseModel):
    cantidad: int
    precioMayorista: int
class insumosPorProducto(BaseModel):
    insumo_Id: str
    cantidad: int
class variaciones(BaseModel):
    codVariacion: str
    descripcion: str
    precioExtra: int
    insumosPorVariacion: list[insumosPorProducto]
class metodoDeCalculo(BaseModel):
    codMetodo: int
    descripcion: str

class product(BaseModel):
    cod_producto : str
    descripcion : str
    precioBase : int
    precioMayoristas : list[pMaroristas]
    insumos : List[insumosPorProducto]
    metodoCalculo: metodoDeCalculo