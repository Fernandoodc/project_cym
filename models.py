from turtle import st
from typing import List, Optional
from mongoengine import Document, StringField
from pydantic import BaseModel, Field
from datetime import datetime

class tokenUser(BaseModel):
    username: str
    codTipoUsuario: int
    nombre: str
    apellido: str

class costoDelivery(BaseModel):
    costoDelivery: int
class senas(BaseModel):
    monto: int

class configuraciones(BaseModel):
    delivery: costoDelivery
    senas: senas

class Usuarios(Document):
    username = StringField()
    password = StringField()

class username(BaseModel):
    username: str

class datosUsuario(username):
    documento: str
    nombre: str
    apellido: str
    celular: str = ''
    Nacionalidades_id: str
    email: str = ''
    direccion : str =''
class changePasw(BaseModel):
    currentPasw: str
    newPasw: str
class newUser(datosUsuario):
    password:str
    codTipoUsuario : int

class clientes(BaseModel):
    documento: str
    nombre: str
    apellido: str
    email: str = ''
    celular: str = ''
    direccion: str = ''
    nacionalidades_id: str
    #saldo: int = 0

class resetPasw(BaseModel):
    userId: str
    newPassword: str

class delivery(BaseModel):
    solicitado : bool = False
    direccion : str = ''

class actInfoPedido(BaseModel):
    fechaEntrega: str
    delivery: delivery

class basePedido(BaseModel):
    fecha: str
    cliente_id : str
    delivery : delivery

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
    profundidad : Optional[float]


class detPedido(BaseModel):
    codPedido : str
    codProducto : str
    medidas : medidas
    descripcion : str = ""
    cantidad : int
    fechaEntrega : str

class editarDet(BaseModel):
    codDetalle: str
    codPedido: str
    descripcion: Optional[str]
    medidas: medidas
    cantidad: Optional[int]

class aprovacion(BaseModel):
    estado: bool
    codProduccion: str

class entregarDetalle(BaseModel):
    fechaEntrega: str = datetime.now().strftime("%Y-%m-%d")
    codDetalle: str
    entregado: bool

class entregarPedido(BaseModel):
    fechaEntrega: str = datetime.now().strftime("%Y-%m-%d")
    codPedido: str
    entregado: bool = True
class proveedores(BaseModel):
    ruc: str
    nombre: str
    direccion: str = ''
    celular: str = ''
    email: str = ''

class facturas(BaseModel):
    fecha: str
    numeroFactura : str
    total: int = 0
    Proveedores_id: str

class insumo(BaseModel):
    descripcion : str
    stockMin : int
    tipoInsumo_id : int

class editInsumo(BaseModel):
    descripcion : str
    stockMin: str

class compraInsumo(BaseModel):
    cantidad : int
    precioUnitario : int
    codInsumo : str
    FacturasProveedores_id : str

class motivoBaja(BaseModel):
    motivo_id: str
    descripcion: Optional[str]

class bajaInsumo(BaseModel):
    fecha : str = datetime.now().strftime("%Y-%m-%d")
    codInsumo: str
    cantidad: int
    motivo: motivoBaja

class datosProduccion(BaseModel):
    codProduccion: str
    cantidad: int

class perdida(BaseModel):
    codInsumo: str
    codProduccion: str
    cantidad: int
    comentarios: str

class pagos(BaseModel):
    fecha: str = datetime.now().strftime("%d-%m-%Y")
    monto: int
    codPedido: str
    cliente_id: str

class factura(BaseModel):
    fecha: str = datetime.now().strftime("%d-%m-%Y")
    codPedido: List[str]
    cliente_id : str

class insumosProducto(BaseModel):
    codInsumo: str
    cantidad: Optional[int]

class precioMayoristas(BaseModel):
    cantidad: int
    precio: int

class metodoCalculo(BaseModel):
    codMetodo: Optional[int] = Field(None, ge=1, le=4)
    descripcion: str = ''

class productos(BaseModel):
    codProducto: Optional[str]
    descripcion: str
    precioBase: int
    insumos_producto: Optional[List[insumosProducto]]
    preciosMayoristas: Optional[List[precioMayoristas]]
    metodoCalculo: metodoCalculo

class tipoEquipo(BaseModel):
    tipo_id: str
    descripcion: Optional[str]

class marcaEquipo(BaseModel):
    marca_id: str
    descripcion: Optional[str]

class mantenimientos(BaseModel):
    fecha: str
    descripcion: str
    Tipos_Mantenimiento_id: str

class tipoMantenimiento(BaseModel):
    tipo_id: str
    descripcion: Optional[str]

class registroMantenimiento(BaseModel):
    idEquipo: str
    fecha: str
    descripcion: str
    tipoMantenimiento : tipoMantenimiento


class equipo(BaseModel):
    numSerie: str
    modelo: str
    fechaAdquisicion: str
    tipoEquipo: tipoEquipo
    marcaEquipo: marcaEquipo

