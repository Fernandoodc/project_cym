from mongo import filter
from fastapi import HTTPException
from fastapi import status
from jose import jwt, JWTError
from config import settings
from models import tokenUser
from datetime import datetime, timedelta
from mongo import agreggate, update_one, find, filter, find_one, delete_one, delete_many
from bson import ObjectId, json_util
from pymongo import MongoClient, ReturnDocument
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
class Login():
    def get_user(self, username: str, codTipoUsuario: int):
        return filter("usuarios", {'username': username, "codTipoUsuario": codTipoUsuario})

    async def get_current_user(self, token: str, required_bool: bool = False):
    
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            scheme, _, param = token.partition(" ")
            payload = jwt.decode(
                param, settings.SECRET_KEY, algorithms=settings.ALGORITHM
            )
            #payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            typeUser: int = payload.get("typeUser")
            print(username)
            if username is None:
                if required_bool:
                    return False
                else: raise credentials_exception
        except Exception as e:
            print(e)
            if required_bool:
                return False
            else: raise credentials_exception

        user = self.get_user(username=username, codTipoUsuario= typeUser)
        if user is None:
            if required_bool:
                return False
            else: raise credentials_exception
        userToken = tokenUser(username=username, typeUser=typeUser)
        return userToken

login = Login()

class Usuarios():
    """
    Get a user from the db
    :param typeRequired: [] , user
    :return: None or one HTTPException(code 403)
    """
    def controlAcceso(self, typeRequired, user):
        if(not user.codTipoUsuario in typeRequired):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes los credenciales necesarios",
                headers={"WWW-Authenticate": "Bearer"},
            )
    def listaUsuarios(self):
        condition = [
            {
                '$lookup':{
                    'from': 'tiposUsuarios',
                    'localField': 'codTipoUsuario',
                    'foreignField': 'codTipo',
                    'as': 'tipoUsuario'
                }
            },
            {
                '$unwind': '$tipoUsuario'
            },
            {
                "$lookup":{
                    'from': 'nacionalidades',
                    'localField': 'Nacionalidades_id',
                    'foreignField': '_id',
                    'as': 'nacionalidad'
                }
            },
            {
                '$unwind': '$nacionalidad'
            }
        ]    
        return db['usuarios'].aggregate(condition)    
    def infoOneUser(self, idUsuario:str):
        condition = [
            {
                "$match":{
                    '_id': ObjectId(idUsuario)
                }
            },
            {
                '$lookup':{
                    'from': 'tiposUsuarios',
                    'localField': 'codTipoUsuario',
                    'foreignField': 'codTipo',
                    'as': 'tipoUsuario'
                }
            },
            {
                '$unwind': '$tipoUsuario'
            },
            {
                "$lookup":{
                    'from': 'nacionalidades',
                    'localField': 'Nacionalidades_id',
                    'foreignField': '_id',
                    'as': 'nacionalidad'
                }
            },
            {
                '$unwind': '$nacionalidad'
            }
        ]
        response =  db['usuarios'].aggregate(condition)  
        for i in response:
            response = i
        return response  
    
    """
    Verifica si un username ya se encuentra en uso, para cambiar el username o agregar uno nuevo
    :param id:str=''(del usuario del cual se quiere consultar), newUsername:str(username por el cual se quiere consultar)
    :return: None o el nombre del usuario ya existente
    """
    def verifUsername(self,newUsername:str, id:str=''):
        condition = {
            'username': newUsername
        }
        if id != '':
            condition["_id"] =  {}
            condition["_id"]['$ne']= ObjectId(id)
        result = db["usuarios"].find_one(condition, {'_id': 0, 'username': 1})
        return result



usuarios = Usuarios()


class Trabajos():
    def trabajos(self):
        hoy = datetime.now()
        mes = hoy - timedelta(days=30)
        data = agreggate("pedidos", [
            {
                "$lookup":{
                    "from": "detallesPedidos",
                    "localField": "codPedido",
                    "foreignField": "codPedido",
                    "as": "pedido"
                }
            },
            {
                "$unwind": "$pedido"
            },
            {
                "$lookup":{
                    "from": "produccion",
                    "localField": "pedido._id",
                    "foreignField": "detallesPedidos_id",
                    "as": "produccion"
                }
            },
            {
                "$unwind": "$produccion"
            },
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "pedido.detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {
                "$unwind": "$producto"
            },
            {
                "$match":{
                    "$or": [{"produccion.etapa.codEtapa": {"$not":{"$eq": 2}}}]
                    #"$or": [{"fecha": { "$gt": str(mes.date()) }}, {"produccion.etapa.codEtapa": {"$not":{"$eq": 2}}}]
                }
            },
            {
                "$project":{
                    "codProduccion": "$produccion.codProduccion",
                    "detallePedido_id": "$pedido._id",
                    "codPedido": "$codPedido",
                    "producto": "$producto.descripcion",
                    "cantidadRestante": "$produccion.cantidadRestante",
                    "cantidad": "$pedido.cantidad",
                    "descripcion": "$descripcion",
                    "fechaEntrega": "$pedido.fechaEntrega",
                    "etapa":{
                        "codEtapa": "$produccion.etapa.codEtapa",
                        "descripcion": "$produccion.etapa.descripcion"
                    }
                }
            }
        ])
        return data
    

    def infoProduccion(self, codDetalle: str):
        condition = [
            {"$match": {
                #"_id":  ObjectId(detallePedidos_id)
                "codProduccion": codDetalle
                }
            },
            {
                "$lookup":{
                    "from": "detallesPedidos",
                    "localField": "detallesPedidos_id",
                    "foreignField": "_id",
                    "as": "detallePedido"
                }
            },
            {
                "$unwind": "$detallePedido"
            },
            {
                "$lookup":{
                    "from": "pedidos",
                    "localField": "detallePedido.codPedido",
                    "foreignField": "codPedido",
                    "as": "infoPedido"
                }
            },
            {
                "$unwind": "$infoPedido"
            },
            {
                "$lookup":{
                    "from": "clientes",
                    "localField": "infoPedido.cliente_id",
                    "foreignField": "_id",
                    "as": "cliente"
                }
            },
            {
                "$unwind": "$cliente"
            },
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "detallePedido.detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {
                "$unwind": "$producto"
            },
            {
                "$project":{
                    "codProduccion": "$codProduccion",
                    "codPedido": "$detallePedido.codPedido",
                    "codDetalle": "$detallePedido.codDetalle",
                    "producto": "$producto.descripcion",
                    "cantidadRestante": "$cantidadRestante",
                    "cantidad": "$detallePedido.cantidad",
                    "descripcion": "$detallePedido.descripcion",
                    "fechaEntrega": "$detallePedido.fechaEntrega",
                    "etapa":{
                        "codEtapa": "$etapa.codEtapa",
                        "descripcion": "$etapa.descripcion"
                    },
                    "archivos": "$detallePedido.archivos",
                    "diseños": "$diseños",
                    "aprovado": "$aprovado",
                    "detalleProducto": "$detallePedido.detalleProducto",
                    "cliente": {
                        "cliente_id": '$cliente._id',
                        "nombre": "$cliente.nombre",
                        "apellido": "$cliente.apellido",
                    }
                }
            }
        ]
        data = agreggate("produccion", condition)
        return data
    def detalleProduccion(self, codProduccion: str):
        """condition = [
            {"$match": {
                "_id":  ObjectId(detallePedidos_id)
                }
            },
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {
                "$unwind": "$producto"
            },
            {
                "$lookup":{
                    "from": "produccion",
                    "localField": "_id",
                    "foreignField": "detallesPedidos_id",
                    "as": "produccion"
                }
            },
            {
                "$unwind": "$produccion"
            },
            {
                "$lookup":{
                    "from": "insumos",
                    "localField": "producto.insumos_producto.codInsumo",
                    "foreignField": "codInsumo",
                    "as": "insumos"
                }
            },
            {
                "$project":{
                    "codProduccion": "$produccion.codProduccion",
                    "codPedido": "$codPedido",
                    "codDetalle": "$codDetalle",
                    "producto": "$producto.descripcion",
                    "etapa":{
                        "codEtapa": "$produccion.etapa.codEtapa",
                        "descripcion": "$produccion.etapa.descripcion"
                    },
                    "cantidadRestante": "$produccion.cantidadRestante",
                    "cantidad": "$cantidad",
                    "descripcion": "$descripcion",
                    "archivos": "$archivos",
                    "diseños": "$produccion.diseños",
                    "detalleProducto": "$detalleProducto",
                    "insumos": "$insumos",
                    "insumos_producto": "$producto.insumos_producto"
                }
            }
        ]"""
        condition = [
            {"$match": {
                "codProduccion":  codProduccion
                }
            },
            {
                "$lookup":{
                    "from": "detallesPedidos",
                    "localField": "detallesPedidos_id",
                    "foreignField": "_id",
                    "as": "detallePedido"
                }
            },
            {
                "$unwind": "$detallePedido"
            },
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "detallePedido.detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {
                "$unwind": "$producto"
            },
            {
                "$lookup":{
                    "from": "insumos",
                    "localField": "producto.insumos_producto.codInsumo",
                    "foreignField": "codInsumo",
                    "as": "insumos"
                }
            },
            {
                "$project":{
                    "codProduccion": "$codProduccion",
                    "codPedido": "$detallePedido.codPedido",
                    "codDetalle": "$detallePedido.codDetalle",
                    "producto": "$producto.descripcion",
                    "etapa":{
                        "codEtapa": "$etapa.codEtapa",
                        "descripcion": "$etapa.descripcion"
                    },
                    "cantidadRestante": "$cantidadRestante",
                    "cantidad": "$detallePedido.cantidad",
                    "descripcion": "$detallePedido.descripcion",
                    "archivos": "$detallePedido.archivos",
                    "diseños": "$diseños",
                    "detalleProducto": "$detallePedido.detalleProducto",
                    "insumos": "$insumos",
                    "insumos_producto": "$producto.insumos_producto"
                }
            }
        ]
        #data = agreggate("detallesPedidos", condition)
        data = agreggate("produccion", condition)
        #print(json_util._json_convert(data)[0])
        for d in data:
            producto = d
        return producto
    #marca la produccion como iniciada y descuenta el stock de lo insumos
    #retorna true si la produccion da inicio
    #retorna false si no hay insumos suficientes
    async def iniciarProduccion(self,codProduccion):
        info = json_util._json_convert(self.detalleProduccion(codProduccion))
        if info['etapa']['codEtapa'] == 0 or info['etapa']['codEtapa'] == 3:

            for insumoProducto in info['insumos_producto']:
                for insumo in info['insumos']:
                
                    if insumoProducto['codInsumo'] == insumo['codInsumo'] and insumo['tipoInsumo_id'] == 1:
                        
                        cantidad = info['cantidadRestante']*insumoProducto['cantidad']
                        if 'stock' in insumo:
                            if cantidad > insumo['stock'] or cantidad <= 0:
                                return False
                            else:
                                break
                        else:
                            return False
            await update_one('produccion', {'codProduccion': codProduccion}, {'$set': {'etapa.codEtapa': 1, 'etapa.descripcion': 'Iniciado'}})
            for insumoProducto in info['insumos_producto']:
                for insumo in info['insumos']:
                    if insumoProducto['codInsumo'] == insumo['codInsumo'] and insumo['tipoInsumo_id'] == 1: 
                        cantidad = info['cantidadRestante'] * insumoProducto['cantidad']
                        await update_one('insumos', {'codInsumo': insumoProducto['codInsumo'], 'tipoInsumo_id': 1},{'$inc': {'stock': -cantidad}})
        return True

    #pasa un datelle a produccion
    def pasarAProduccion(self, codDetalle):
        pedido = json_util._json_convert(find_one('detallesPedidos', {'codDetalle': codDetalle}))
        if filter('produccion', {'detallesPedidos_id': ObjectId(pedido['_id']['$oid'])}) == None:
            data = {
                        "codProduccion": pedido['codDetalle'],
                        "detallesPedidos_id": ObjectId(pedido['_id']['$oid']),
                        "cantidadRestante": pedido['cantidad'],
                        "etapa":{
                            'codEtapa': 0,
                            'descripcion': "No Iniciado"
                        }
                    }
            db['produccion'].insert_one(data)
    def pasarTodoAProduccion(self, codPedido):
        pedidos = json_util._json_convert(find('detallesPedidos', {'codPedido': codPedido}))
        for pedido in pedidos:
            self.pasarAProduccion(pedido['codDetalle'])
    async def deleteAllOfProduccion(self, codPedido):
        detalles = find('detallesPedidos', {'codPedido': codPedido})
        for i in detalles:
            if find_one('produccion', {'detallesPedidos_id': ObjectId(i['_id'])}) == None:
                break
            await delete_one('produccion', {'detallesPedidos_id': ObjectId(i['_id'])})
    
    #retorna el estado de la produccion de todos lo detalles de un grupo de un pedido, y un boolean de si
    #ya la produccion de todos los detalles ya fue terminada
    '''return = {
        codPedido: str,
        detallesPedidos:{
            codDetalle: str,
            produccion: {
                codProduccion: str,
                etapa: {
                    codEtapa: int
                    descripcion: str
                },
                cantidadRestante: int

            }
        },
        produccionTerminada: bool (de si toda las producciones ya fueron terminadas)
    }'''
    def estadoProduccionPedido(self, codPedido: str):
        condition = [
            {'$match': {
                'codPedido': codPedido
            }},
            {
                '$lookup':{
                    'from': 'produccion',
                    'localField': '_id',
                    'foreignField': 'detallesPedidos_id',
                    'as': 'produccion'
                }
            },
            {'$unwind': '$produccion'},
            {
                '$project':{
                    '_id': 0,
                    'codDetalle': 1,
                    'produccion.codProduccion': 1,
                    'produccion.etapa': 1,
                    'produccion.cantidadRestante': 1

                }
            }
        ]
        produccionTerminada = False
        produccion = json_util._json_convert(db["detallesPedidos"].aggregate(condition))
        for i in produccion:
            print(i['produccion'])
            if i['produccion']['etapa']['codEtapa'] == 2:
                produccionTerminada = True
            else:
                produccionTerminada = False
                break
        response = {
            'codPedido': codPedido,
            'detallesPedido': produccion,
            'produccionTerminada': produccionTerminada
        }
        return response

trabajos = Trabajos()

class Pedidos():
    #retorna la info del cliente de un pedido
    def infoCliente(self, codPedido):
        datosCliente = agreggate('pedidos', [
            {"$match": {
                "codPedido":  codPedido
                }
            },
            {
                "$lookup":{
                    "from": "clientes",
                    "localField": "cliente_id",
                    "foreignField": "_id",
                    "as": "cliente"
                }
            },
            {
                "$unwind": "$cliente"
            },
            {
                "$project":{
                    "cliente": "$cliente",
                    "total": "$presupuesto"
                }
            }

        ])

        for i in datosCliente:
            cliente = i
        return cliente

    #retorna info basica y general del grupo de pedido
    def infoPedido(self, codPedido):
        pedido = find_one('pedidos', {'codPedido': codPedido})
        return pedido

    #retorna la info completa e individual de cada detalle de pedido, incluyendo los datos del producto
    #return [{},{}]
    def infoDetalle(self, codPedido):
        condition = [
            {"$match": {
                "codPedido":  codPedido
                }
            },
            {
                "$lookup":{
                    "from": "detallesPedidos",
                    "localField": "codPedido",
                    "foreignField": "codPedido",
                    "as": "pedido"
                }
            },
            {"$unwind": "$pedido"},
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "pedido.detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {"$unwind": "$producto"}

        ]
        pedidos = agreggate("pedidos", condition)
        return pedidos

    #retorna toda la info de los detalles de un pedido incluyendo info del producto y excluyendo la info del grupo de pedidos
    def infoDetallePedido(self, codPedido):
        condition = [
            {"$match": {
                "codPedido":  codPedido
                }
            },
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {"$unwind": "$producto"}
        ]
        response = db["detallesPedidos"].aggregate(condition)
        return response

    def infoOneDetalle(self, codDetalle):
        condition = [
            {"$match": {
                "codDetalle":  codDetalle
                }
            },
            {
                "$lookup":{
                    "from": "pedidos",
                    "localField": "codPedido",
                    "foreignField": "codPedido",
                    "as": "pedido"
                }
            },
            {"$unwind": "$pedido"},
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {"$unwind": "$producto"},
            {'$lookup':{
                'from': 'produccion',
                'localField': '_id',
                'foreignField': 'detallesPedidos_id',
                'as': 'produccion'
            }},
            {'$unwind': '$produccion'},
            {'$lookup':{
                'from': 'clientes',
                'localField': 'pedido.cliente_id',
                'foreignField': '_id',
                'as': 'cliente'
            }},
            {'$unwind': '$cliente'},

            {
                '$project':{
                    'produccion.diseños': 0,
                    'produccion.aprovado': 0,
                    'produccion.detallesPedidos_id': 0
                }
            }

        ]
        respose = agreggate('detallesPedidos', condition)
        for i in respose:
            respose = i

        estadoCuenta = db['cuentas'].find_one({'codPedido': respose['codPedido']}, {'total': 1, 'saldo': 1, '_id': 0})
        respose['estadoCuenta'] = estadoCuenta
        produccionPedido = trabajos.estadoProduccionPedido(respose['codPedido'])
        respose['produccionPedido'] = {}
        respose['produccionPedido']['produccionTerminada'] = produccionPedido['produccionTerminada']
        return i
    #return: [{}] -> infoGrupo, infoCliente, detallesPedido
    def infoFullAllPedidos(self):
        condition = [
            {
                "$lookup":{
                    "from": "clientes",
                    "localField": "cliente_id",
                    "foreignField": "_id",
                    "as": "cliente"
                }
            },
            {"$unwind": "$cliente"},
            {
                "$lookup":{
                    "from": "detallesPedidos",
                    "localField": "codPedido",
                    "foreignField": "codPedido",
                    "as": "pedido"
                }
            },
            {"$unwind": "$pedido"},
            {
                "$lookup":{
                    "from": "produccion",
                    "localField": "pedido._id",
                    "foreignField": "detallesPedidos_id",
                    "as": "produccion"
                }
            },
            
            {
                "$lookup":{
                    "from": "productos",
                    "localField": "pedido.detalleProducto.codProducto",
                    "foreignField": "codProducto",
                    "as": "producto"
                }
            },
            {"$unwind": "$producto"},
        ]
        pedidos = agreggate("pedidos", condition)
        return pedidos

    def sumPresupuesto(self, codPedido):
        condition = [
            { "$match": {
                'codPedido': codPedido
                }
            },
            {"$group":{
                "_id": '',
                "presupuesto": { "$sum": "$presupuesto" },
                "descuento": { "$sum": "$descuento" },
                "subTotal": { "$sum": "$subTotal" }
                }
            },
            {
                "$project":{
                    "_id": 0,
                    "subTotal": "$subTotal",
                    "descuento": "$descuento",
                    "presupuesto": "$presupuesto"
                }
            }
        ]
        response = db['detallesPedidos'].aggregate(condition)
        #print(json_util._json_convert(response))
        for i in response:
            response = i
        #print(json_util._json_convert(response))
        return response

    async def eliminarPedido(self, codPedido:str):
        info = json_util._json_convert(db['pedidos'].find_one({'codPedido': codPedido}))
        db['clientes'].update_one({'_id': ObjectId(info['cliente_id']['$oid'])}, {"$inc": {'saldo': -info['presupuesto']}})
        """if info['infoDelivery']['solicitado'] == True:
            db['clientes'].update_one({'_id': ObjectId(info['cliente_id']['$oid'])}, {"$inc": {'saldo': -info['infoDelivery']['costoDelivery']}})"""
        await delete_one('pedidos', {'codPedido': codPedido })
        await delete_one('cuentas', {'codPedido': codPedido })
        await delete_many('detallesPedidos', {'codPedido': codPedido})
    def actPresupuesto(self, codPedido:str):
        presupuestoAct = self.sumPresupuesto(codPedido)
        aux = False
        if not 'presupuesto' in presupuestoAct:
            presupuestoAct = {
                "subTotal": 0,
                "descuento": 0,
                "presupuesto": 0
            }
            #bandera que informa que se elimino el ultimo detalle del pedido
            aux = True
        db['pedidos'].update_one({'codPedido': codPedido}, {'$set':presupuestoAct})
        presupuestoAct = presupuestoAct['presupuesto']
        inforDelivery= self.infoPedido(codPedido)['infoDelivery']
        if aux == False:
            if inforDelivery['solicitado'] == True:
                db['pedidos'].update_one({'codPedido': codPedido}, {'$inc':{'presupuesto': inforDelivery['costoDelivery']}})
                presupuestoAct = presupuestoAct + inforDelivery['costoDelivery']
        db['cuentas'].find_one_and_update({'codPedido': codPedido}, {'$set':{'total': presupuestoAct}}, return_document=ReturnDocument.AFTER)
        cuentas = db['cuentas'].find_one({'codPedido': codPedido})
        db["clientes"].update_one({'_id': ObjectId(cuentas['cliente_id'])}, {'$inc':{'saldo': -cuentas['saldo']}})
        monto = 0
        vuelto = 0
        response = 0
        if 'pagos'in cuentas:
            for pago in cuentas['pagos']:
                monto = monto + pago['monto']
            seq = db['seq'].find_one_and_update({"cod": 2}, {"$inc":{"seq": 1}}, upsert=True , return_document=ReturnDocument.AFTER)
            numRecibo = '0'*(settings.NUM_RECIBO - len(str(seq['seq']))) + str(seq["seq"])
            if monto > presupuestoAct:
                if aux == True:
                    db['cuentas'].update_one({'codPedido': codPedido}, { '$unset': { 'pagos': "" }})
                else:
                    datos = {
                        "fecha" : datetime.now().strftime("%y-%m-%d"),
                        "monto": presupuestoAct,
                        "saldo": 0,
                        "numeroRecibo": numRecibo
                    }
                    db['cuentas'].update_one({'codPedido': codPedido}, {"$set":{'pagos': [datos]}})
            else:
                datos = {
                        "fecha" : datetime.now().strftime("%y-%m-%d"),
                        "monto": monto,
                        "saldo": presupuestoAct-monto,
                        "numeroRecibo": numRecibo
                    }
                db['cuentas'].update_one({'codPedido': codPedido}, {"$set":{'pagos': [datos]}})
            response = numRecibo
        if (presupuestoAct- monto) <= 0:
            vuelto = monto - presupuestoAct
            saldo = 0
            db['cuentas'].update_one({'codPedido': codPedido}, {"$set":{"saldo": 0}})
            db["clientes"].update_one({'_id': ObjectId(cuentas['cliente_id'])}, {'$inc':{'saldo': 0}})
        else:
            saldo = presupuestoAct - monto
            db['cuentas'].update_one({'codPedido': codPedido}, {"$set":{"saldo": (presupuestoAct-monto)}})
            db["clientes"].update_one({'_id': ObjectId(cuentas['cliente_id'])}, {'$inc':{'saldo': (presupuestoAct-monto)}})
        return {'numeroRecibo': response,
        'saldo': saldo,
        'vuelto': vuelto}

    #informa si todos los detalles de un pedidos ya fueron entregados
    #return = bool
    def estadoEntrega(self, codPedido):
        entregados = False
        detalles = json_util._json_convert(db['detallesPedidos'].find({'codPedido': codPedido}))
        for detalle in detalles:
            if 'entrega' in detalle:
                if detalle['entrega']['entregado'] == True:
                    entregados = True
                else:
                    entregados = False
                    break
        return entregados
infoPedidos = Pedidos()


class Insumos():
    def infoAllInsumos(self):
        condition = [
                {
                    "$lookup":{
                        "from": "tiposInsumos",
                        "localField": "tipoInsumo_id",
                        "foreignField": "_id",
                        "as": "tipoInsumo"
                    }
                },
                {
                    "$unwind": "$tipoInsumo"
                },
                {
                    "$project":{
                        "_id": 0,
                        "tipoInsumo_id": 0
                    }
                }
        ]
        respones = db['insumos'].aggregate(condition)
        return respones
    async def reponerStock(self, codProduccion):
        info = json_util._json_convert(trabajos.detalleProduccion(codProduccion))
        for insumoProducto in info['insumos_producto']:
            for insumo in info['insumos']:
                if insumoProducto['codInsumo'] == insumo['codInsumo'] and insumo['tipoInsumo_id'] == 1:
                    cantidad = insumoProducto['cantidad']*info['cantidadRestante']
                    await update_one('insumos', {'codInsumo': insumoProducto['codInsumo'], 'tipoInsumo_id': 1},{'$inc': {'stock': cantidad}})
        perdidos = json_util._json_convert(find('insumosPerdidos', {'Produccion_id': info['codProduccion']}))
        """if perdidos != None:
            for perdido in perdidos:
                update_one('insumos', {'codInsumo': perdido['Insumos_id']}, {'$inc': {'stock': -perdido['cantidad']}})"""

    #retorna los insumos perdidos en una produccion
    #sin no se envia codProduccion retorna el historial de insumos perdidos
    def insumosPerdidos(self, codProduccion = None):
        if codProduccion == None:
            condicion = [
                {
                    "$lookup":{
                        "from": "insumos",
                        "localField": "Insumos_id",
                        "foreignField": "codInsumo",
                        "as": "insumo"
                    }
                },
                {
                    "$unwind": "$insumo"
                },
                {
                    "$project":{
                        "comentarios": "$comentarios",
                        "fecha": "$fecha",
                        "cantidad": "$cantidad",
                        "insumo": "$insumo",
                        "Produccion_id": "$Produccion_id"
                    }
                }
            ]
        else:

            condicion = [
                {"$match": {
                    "Produccion_id":  codProduccion
                    }
                },
                {
                    "$lookup":{
                        "from": "insumos",
                        "localField": "Insumos_id",
                        "foreignField": "codInsumo",
                        "as": "insumo"
                    }
                },
                {
                    "$unwind": "$insumo"
                },
                {
                    "$project":{
                        "comentarios": "$comentarios",
                        "fecha": "$fecha",
                        "cantidad": "$cantidad",
                        "insumo": "$insumo",
                        "Produccion_id": "$Produccion_id"
                    }
                }
            ]
        response = agreggate('insumosPerdidos', condicion)
        return response

    
insumos = Insumos()

class Productos():
    def infoProducto(self, codProducto):
        return db['productos'].find_one({'codProducto': codProducto})

    def infoInsumos(self, codProducto: str):
        condicion = [
            {"$match": {
                "codProducto":  codProducto
                }
            },
            {
                "$lookup":{
                    "from": "insumos",
                    "localField": "insumos_producto.codInsumo",
                    "foreignField": "codInsumo",
                    "as": "insumo"
                }
            },
            {
                '$unwind': '$insumo'
            },
            {
                '$project': {
                    'datos': '$insumos_producto',
                    'insumo': '$insumo'
                }
            }
        ]
        response = db['productos'].aggregate(condicion)
        return response
    '''
    Comtrol para saber si no hay ninguna producción sin terminar o pedido sin entregar relacionado a este productos
    Para saber si se puede proceder a eliminar el productos
    :return: bool
    true = se puede eliminar ; false = no se puede eliminar
    '''
    def controlDelete(self, CodProducto:str):
        condition = [
            {
                '$match':{'detalleProducto.codProducto': CodProducto}
            },
            {
                '$lookup':{
                'from': 'productos',
                'localField': 'detalleProducto.codProducto',
                'foreignField': 'codProducto',
                'as': 'producto'
                }
            },
            {
                '$unwind': '$producto'
            },
            {
                '$lookup':{
                'from': 'produccion',
                'localField': '_id',
                'foreignField': 'detallesPedidos_id',
                'as': 'produccion'
                }
            },
            {
                '$unwind': '$produccion'
            },
            {
                '$match': {
                '$or': [{'entrega.entregado': False},
                {'produccion.etapa.codEtapa': {'$ne': 2}}]
                }
            },
            {
                '$count': 'cantidad'
            }
        ]
        cant = json_util._json_convert(db['detallesPedidos'].aggregate(condition))
        for i in cant:
            cant = i
        if 'cantidad' in cant:
            if cant['cantidad']>0:
                return False
        return True


infoProductos = Productos()

class Clientes():

    def deudas(self, documento : str):
        cliente = db["clientes"].find_one({'documento': documento})
        if cliente == None:
            return None
        idCliente = cliente['_id']
        condition = [
            {"$match": {
                "cliente_id":  idCliente,
                "saldo": {'$gt': 0}
                }
            },
            {
                "$lookup":{
                    "from": "pedidos",
                    "localField": "codPedido",
                    "foreignField": "codPedido",
                    "as": "pedido"
                }
            },
            {
                '$unwind': '$pedido'
            },
        

            {
                '$project':{
                    '_id': 0,
                    'codPedido': '$codPedido',
                    'saldo': '$saldo',
                    'total': '$total',
                    'pagos': '$pagos',
                    'pedido': {
                        'fecha': '$pedido.fecha',
                        'presupuesto': '$pedido.presupuesto',
                        'descuento': '$pedido.descuento',
                        'subTotal': '$pedido.subTotal',
                        #'detallesPedido': '$detallesPedido',
                        #'producto': '$productos'

                    },

                }
            }
        
        ]
        cuentas = db['cuentas'].aggregate(condition)
        cuentas = json_util._json_convert(cuentas)
        for i in range(0,len(cuentas)):
            detalle = infoPedidos.infoDetallePedido(cuentas[i]['codPedido'])
            cuentas[i]['detallesPedido'] = detalle

        response = {
            'datosCliente': cliente,
            'cuentas': cuentas
        }
        #print(json_util._json_convert(cuentas))
        return response

    def pagos(self, _id: str):
        cliente = db["clientes"].find_one({'_id':  ObjectId(_id)})
        condition = [
            {"$match": {
                "cliente_id":  ObjectId(_id),
                }
            },
            {
                "$lookup":{
                    "from": "pedidos",
                    "localField": "codPedido",
                    "foreignField": "codPedido",
                    "as": "pedido"
                }
            },
            {
                '$unwind': '$pedido'
            },
        

            {
                '$project':{
                    '_id': 0,
                    'codPedido': '$codPedido',
                    'saldo': '$saldo',
                    'total': '$total',
                    'pagos': '$pagos',
                    'pedido': {
                        'fecha': '$pedido.fecha',
                        'presupuesto': '$pedido.presupuesto',
                        'descuento': '$pedido.descuento',
                        'subTotal': '$pedido.subTotal',

                    },

                }
            }
        
        ]
        cuentas = db['cuentas'].aggregate(condition)
        cuentas = json_util._json_convert(cuentas)
        for i in range(0,len(cuentas)):
            detalle = infoPedidos.infoDetallePedido(cuentas[i]['codPedido'])
            cuentas[i]['detallesPedido'] = detalle
        response = {
            'datosCliente': cliente,
            'cuentas': cuentas
        }
        return response

    def pedidos(self, _id:str):
        cliente = db["clientes"].find_one({'_id':  ObjectId(_id)})
        pedidos = db["pedidos"].find({'cliente_id': ObjectId(_id)})
        pedidos = json_util._json_convert(pedidos)
        for i in range(0,len(pedidos)):
            detalle = infoPedidos.infoDetallePedido(pedidos[i]['codPedido'])
            pedidos[i]['detallesPedido'] = detalle
        
        response = {
            'datosCliente': cliente,
            'pedidos': pedidos
        }
        return response

clientes = Clientes()

class Equipos():
    # return =[{
    #   _id: ObjectId
    #   numSerie: str,
    #   modelo: str,
    #   fechaAdquisicion: str,
    #   marcaEquipo: {_id: ObjectId, descripcion: str },
    #   tipoEquipo: {_id: ObjectId, descripcion: str}
    #   mantenimientos: [{
    #      fecha: str, descripcion: str
    #   }]
    # }]
    def datosEquipos(self):
        condition = [
            {
                "$lookup":{
                    "from": "marcasEquipos",
                    "localField": "Marcas_Equipos_id",
                    "foreignField": "_id",
                    "as": "marcaEquipo"
                }
            },
            {
                "$unwind": "$marcaEquipo"
            },
            {
                "$lookup":{
                    "from": "tiposEquipos",
                    "localField": "Tipos_Equipos_id",
                    "foreignField": "_id",
                    "as": "tipoEquipo"
                }
            },
            {
                "$unwind": "$tipoEquipo"
            },
            {
                '$project':{
                    'Tipos_Equipos_id': 0,
                    'Marcas_Equipos_id': 0,

                }
            }
        ]
        response = db['equipos'].aggregate(condition)
        return response
    # return =[{
    #   _id: ObjectId
    #   numSerie: str,
    #   modelo: str,
    #   fechaAdquisicion: str,
    #   marcaEquipo: {_id: ObjectId, descripcion: str },
    #   tipoEquipo: {_id: ObjectId, descripcion: str}
    #   mantenimientos: [{
    #      fecha: str, descripcion: str, Tipos_Mantenimiento_id : ObjectId
    #   }]
    # }]
    def datoEquipo(self, id):
        condition = [
            {
                '$match':{
                    '_id': ObjectId(id)
                }
            },
            {
                "$lookup":{
                    "from": "marcasEquipos",
                    "localField": "Marcas_Equipos_id",
                    "foreignField": "_id",
                    "as": "marcaEquipo"
                }
            },
            {
                "$unwind": "$marcaEquipo"
            },
            {
                "$lookup":{
                    "from": "tiposEquipos",
                    "localField": "Tipos_Equipos_id",
                    "foreignField": "_id",
                    "as": "tipoEquipo"
                }
            },
            {
                "$unwind": "$tipoEquipo"
            },
        ]
        response = db['equipos'].aggregate(condition)
        for i in response:
            response = i
        return response
    
    def mantenimientos(self):
        equipos = json_util._json_convert(self.datosEquipos())
        print(equipos)
        for i in range(0,len(equipos)):
            if 'Mantenimientos' in equipos[i]:
                for j in range(0, len(equipos[i]['Mantenimientos'])):
                    mant = db['tiposMantenimiento'].find_one({'_id': ObjectId(equipos[i]['Mantenimientos'][j]['Tipos_Mantenimiento_id']['$oid'])})
                    equipos[i]['Mantenimientos'][j]['mantenimiento'] = mant

        return equipos
    def mantenimientosOneEquipo(self, id):
        equipos = json_util._json_convert(self.datoEquipo(id))
        print(equipos)
        if 'Mantenimientos' in equipos:
            for j in range(0, len(equipos['Mantenimientos'])):
                mant = db['tiposMantenimiento'].find_one({'_id': ObjectId(equipos['Mantenimientos'][j]['Tipos_Mantenimiento_id']['$oid'])})
                equipos['Mantenimientos'][j]['mantenimiento'] = mant
        return equipos
  
equipos = Equipos()

class funcionesReportes():
    class Pedidos():
        def noEntregados(self, fInicio:str='' , fFin:str=''):
            condition = [
                {
                    "$lookup":{
                        "from": "clientes",
                        "localField": "cliente_id",
                        "foreignField": "_id",
                        "as": "cliente"
                    }
                },
                {"$unwind": "$cliente"},
                {
                    "$lookup":{
                        "from": "detallesPedidos",
                        "localField": "codPedido",
                        "foreignField": "codPedido",
                        "as": "pedido"
                    }
                },
                {"$unwind": "$pedido"},
                {
                    "$lookup":{
                        "from": "produccion",
                        "localField": "pedido._id",
                        "foreignField": "detallesPedidos_id",
                        "as": "produccion"
                    }
                },
                {"$unwind": "$produccion"},
                {
                    "$lookup":{
                        "from": "productos",
                        "localField": "pedido.detalleProducto.codProducto",
                        "foreignField": "codProducto",
                        "as": "producto"
                    }
                },
                {"$unwind": "$producto"},
                {'$match':{                    
                    'produccion.etapa.codEtapa': 2,
                    'pedido.entrega.entregado': False
                    }
                }
            ]
            if fInicio != '':
                condition.append({
                    '$match': {
                        "fecha": { "$gte": fInicio }
                    }
                })
            if fFin != '':
                condition.append({
                    '$match':{
                        "fecha": { "$lte": fFin }
                    }
                })
            response = db['pedidos'].aggregate(condition)
            return response

        def resumen(self, fInicio:str='' , fFin:str='', codEntrega:int=''):
            condition = [
                {
                    '$lookup':{
                    'from': 'pedidos',
                    'localField': 'codPedido',
                    'foreignField': 'codPedido',
                    'as': 'pedido'
                    }
                },
                {
                    '$group':{
                        '_id': '$detalleProducto.codProducto',
                        'cantidad': {'$sum': '$cantidad'},
                        'presupuesto': {'$sum': '$presupuesto'}
                    }
                },
                {
                    '$lookup':{
                        'from': 'productos',
                        'localField': '_id',
                        'foreignField': 'codProducto',
                        'as': 'producto'
                    }
                },
                {
                    '$unwind': '$producto'
                },
                {
                    '$project':{
                    'codProducto': '$_id',
                    'cantidad': '$cantidad',
                    'descripcion': '$producto.descripcion',
                    'presupuesto': '$presupuesto'
                    }
                }
            ]
            aux = 1
            if codEntrega == 0:
                condition.insert(0, 
                {
                    '$match':{
                    'entrega.entregado': True
                    }
                })
                aux = 2
            elif codEntrega == 1:
                condition.insert(0,
                {
                    '$match':{
                    'entrega.entregado': False
                    }
                })
                aux = 2
            if fInicio != '':
                condition.insert(aux,{
                    '$match': {
                        "pedido.fecha": { "$gte": fInicio }
                    }
                })
            if fFin != '':
                condition.insert(2,{
                    '$match':{
                        "pedido.fecha": { "$lte": fFin }
                    }
                })
            
            
            
            return db["detallesPedidos"].aggregate(condition)
    class Insumos():
        def perdidosDet(self, fInicio:str='' , fFin:str=''):
            condition = [
                {
                    '$lookup':{
                    "from": 'insumos',
                    'localField': 'Insumos_id',
                    'foreignField': 'codInsumo',
                    'as': 'insumo'
                    }
                },
                {
                    '$unwind': '$insumo'
                }
            ]
            if fInicio != '':
                condition.append({
                    '$match': {
                        "fecha": { "$gte": fInicio }
                    }
                })
            if fFin != '':
                condition.append({
                    '$match':{
                        "fecha": { "$lte": fFin }
                    }
                })
            return db['insumosPerdidos'].aggregate(condition)
        def perdidosRes(self, fInicio:str='' , fFin:str=''):
            condition = [
                {
                    '$group':{
                        '_id': '$Insumos_id',
                        'cantidad': {'$sum': '$cantidad'}
                    }
                },
                {
                    '$lookup':{
                    "from": 'insumos',
                    'localField': '_id',
                    'foreignField': 'codInsumo',
                    'as': 'insumo'
                    }
                },
                {
                    '$unwind': '$insumo'
                },
                {
                    '$project':{
                        '_id': 0,
                        'codInsumo': '$_id',
                        'descripcion': '$insumo.descripcion',
                        'cantidad': '$cantidad'
                    }
                }
            ]
            if fInicio != '':
                condition.insert(0, {
                    '$match': {
                        "fecha": { "$gte": fInicio }
                    }
                })
            if fFin != '':
                condition.insert(0,{
                    '$match':{
                        "fecha": { "$lte": fFin }
                    }
                })
            return db['insumosPerdidos'].aggregate(condition)
        def utilizados(self, fInicio:str='' , fFin:str=''):
            condition = [
                {
                    '$lookup':{
                    'from': 'pedidos',
                    'localField': 'codPedido',
                    'foreignField': 'codPedido',
                    'as': 'pedido'
                    }
                },
                {
                    '$unwind': '$pedido'
                },
                {
                    '$lookup':{
                    'from': 'productos',
                    'localField': 'detalleProducto.codProducto',
                    'foreignField': 'codProducto',
                    'as': 'producto'
                    }
                },
                {
                    '$unwind': '$producto'
                },
                {
                    '$unwind': '$producto.insumos_producto'
                },
                {
                    '$group':{
                    '_id': '$producto.insumos_producto.codInsumo',
                    'cantidad': {'$sum': {'$multiply': ['$cantidad', '$producto.insumos_producto.cantidad']}}
                    }
                },
                {
                    '$lookup':{
                        'from': 'insumos',
                        'localField': '_id',
                        'foreignField': 'codInsumo',
                        'as': 'insumo'
                    }
                },
                {
                    '$unwind': '$insumo'
                },
                {
                    '$match':{
                        'insumo.tipoInsumo_id': 1
                    }
                },
                {
                    '$project':{
                        '_id': 0,
                        'codInsumo': '$_id',
                        'descripcion': '$insumo.descripcion',
                        'cantidad': '$cantidad'
                    }
                }
                ]
            if fInicio != '':
                condition.insert(2 ,{
                    '$match': {
                        "pedido.fecha": { "$gte": fInicio }
                    }
                })
            if fFin != '':
                condition.insert(2, {
                    '$match':{
                        "pedido.fecha": { "$lte": fFin }
                    }
                })
            return db["detallesPedidos"].aggregate(condition)
        def historialDet(self,  fInicio:str='' , fFin:str=''):
            condition = [
                {
                    '$lookup': {
                        'from': 'insumos',
                        'localField': 'codInsumo',
                        'foreignField': 'codInsumo',
                        'as': 'insumo'
                    }
                },
                {
                    '$unwind': '$insumo'
                },
                {
                    '$lookup':{
                        'from': 'facturasProveedores',
                        'localField': 'FacturasProveedores_id',
                        'foreignField': '_id',
                        'as': 'factura'
                    }
                },
                {
                    '$unwind': '$factura'
                },
                {
                    '$lookup':{
                        'from': 'proveedores',
                        'localField': 'factura.Proveedores_id',
                        'foreignField': '_id',
                        'as': 'proveedor'
                    }
                },
                {
                    '$unwind': '$proveedor'
                }
            ]
            if fInicio != '':
                condition.append({
                    '$match': {
                        "factura.fecha": { "$gte": fInicio }
                    }
                })
            if fFin != '':
                condition.append({
                    '$match':{
                        "factura.fecha": { "$lte": fFin }
                    }
                })
            return db['comprasInsumos'].aggregate(condition)

class Auditorias():
    def productos(self):
        condition = [
            {
                '$lookup':{
                    'from': 'usuarios',
                    'localField': 'usuario',
                    'foreignField': '_id',
                    'as': 'infoUsuario'
                }
            },
            {
                '$unwind': '$infoUsuario'
            }
        ]
        return db['auditoriaProductos'].aggregate(condition)
    def pedidos(self):
        condition = [
            {
                '$lookup':{
                    'from': 'usuarios',
                    'localField': 'usuario',
                    'foreignField': '_id',
                    'as': 'infoUsuario'
                }
            },
            {
                '$unwind': '$infoUsuario'
            }
        ]
        return db['auditoriaPedidos'].aggregate(condition)
    def insumos(self):
        condition = [
            {
                '$lookup':{
                    'from': 'usuarios',
                    'localField': 'usuario',
                    'foreignField': '_id',
                    'as': 'infoUsuario'
                }
            },
            {
                '$unwind': '$infoUsuario'
            }
        ]
        return db['auditoriaInsumos'].aggregate(condition)
    def detallesPedidos(self):
        condition = [
            {
                '$lookup':{
                    'from': 'usuarios',
                    'localField': 'usuario',
                    'foreignField': '_id',
                    'as': 'infoUsuario'
                }
            },
            {
                '$unwind': '$infoUsuario'
            }
        ]
        return db['auditoriaDetallesPedidos'].aggregate(condition)
    def proveedores(self):
        condition = [
            {
                '$lookup':{
                    'from': 'usuarios',
                    'localField': 'usuario',
                    'foreignField': '_id',
                    'as': 'infoUsuario'
                }
            },
            {
                '$unwind': '$infoUsuario'
            }
        ]
        return db['auditoriaProveedores'].aggregate(condition)
        

