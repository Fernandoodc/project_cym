from bson import ObjectId
from turtle import st
from typing import List
from mongoengine import Document, StringField
from pydantic import BaseModel
import datetime

class tokenUser(BaseModel):
    username: str
    typeUser: int

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
    precio: int
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
    codProducto : str
    descripcion : str = ""
    precioBase : int
    preciosMayoristas : list[pMaroristas]
    insumos : List[insumosPorProducto]
    metodoCalculo: metodoDeCalculo

class basePedido(BaseModel):
    fecha: str
    cliente_id : str
class pedidos(basePedido):
    codPedido : str = ""
    subtotal : int
    descuento : int
    total : int = 0
    presupuesto : int

class actPresu(BaseModel):
    codPedido: str
    subTotal : int
    descuento : int
    presupuesto : int

class medidas(BaseModel):
    ancho : float = 0
    alto : float = 0
    profundidad : float = 0

class detPedido(BaseModel):
    codPedido : str
    codProducto : str
    medidas : medidas
    descripcion : str = ""
    cantidad : int
    fechaEntrega : str
    delivery : bool
