from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from bson import json_util, ObjectId
import models
from pymongo import MongoClient, errors, ReturnDocument
import datetime
import json
from manager import	 manager
from mongo import delete_one, delete_many, find_one, find, update_one
from functions import infoPedidos, trabajos
from config import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
Pedidos = APIRouter()

templates = Jinja2Templates(directory="templates")

def actPresuPedido(pedido: models.actPresu):
    filter = {'codPedido': pedido.codPedido}
    newvalues = { '$inc': {'subTotal': pedido.subTotal,
    'descuento': pedido.descuento,
    'presupuesto': pedido.presupuesto
    }}
    db['pedidos'].find_one_and_update(filter=filter, update=newvalues, upsert=True)
    #db['pedidos'].update_one(filter, newvalues)
    return 'ok'


@Pedidos.get("/pedidos")
async def pedidos(request: Request, codDetalle:str = '', user=Depends(manager)):
    pedidos = infoPedidos.infoFullAllPedidos()
    return templates.TemplateResponse("pedidos.html", context={"request": request, 'pedidos': pedidos, 'codDetalle': codDetalle,  'userInfo': user})


@Pedidos.get('/')
async def listaPedidos(response: Response, user=Depends(manager)):
    pedidos = json_util._json_convert(infoPedidos.infoFullAllPedidos())
    return pedidos

@Pedidos.get('/nuevo_pedido')
async def nuevo_pedido(request: Request, user=Depends(manager)):
    productos =json_util._json_convert(db['productos'].find())
    delivery = json_util._json_convert(db['configuraciones'].find_one())
    nacionalidades = json_util._json_convert(db['nacionalidades'].find())
    return templates.TemplateResponse('cym_nuevo_pedido.html', context={'request': request, 'productos': productos, 'delivery' : delivery['delivery'], 'nacionalidades': nacionalidades, 'userInfo': user})    


@Pedidos.post('/create_pedido', status_code=status.HTTP_201_CREATED)
async def createPedido(pedido: models.basePedido, response: Response, user=Depends(manager)):
    date = datetime.datetime.now().strftime("%y%m")
    seq = db['seqPedidos'].find_one_and_update({"date": date}, {"$inc":{"seq": 1}}, upsert = True, return_document=ReturnDocument.AFTER)
    delivery = 0
    if (pedido.delivery.solicitado == True):
        delivery = db['configuraciones'].find_one()['delivery']['costoDelivery']
    codPedido = str(date)+str(seq['seq'])
    data = {
        "codPedido": codPedido,
        "fecha": pedido.fecha,
        "cliente_id": ObjectId(pedido.cliente_id),
        'infoDelivery': {
            'solicitado': pedido.delivery.solicitado,
            'costoDelivery': delivery,
            'direccion': pedido.delivery.direccion
        },
        "presupuesto": delivery
    }
    db['pedidos'].insert_one(data)
    db['cuentas'].insert_one({"cliente_id": ObjectId(pedido.cliente_id), "codPedido": codPedido, 'saldo': delivery, 'total': delivery})
    db['clientes'].update_one({'_id': ObjectId(pedido.cliente_id)}, {"$inc": {'saldo': delivery}}, upsert=True)
    return {'msg' : "success",
    "codPedido": codPedido
    }


@Pedidos.post('/agg_detpedido', status_code=status.HTTP_201_CREATED)
async def aggDetPedido(response: Response, detalle:models.detPedido, user=Depends(manager)):
    prod = db['productos'].find_one({'codProducto': detalle.codProducto})
    metCal = prod['metodoCalculo']['codMetodo']
    predMayo = prod['preciosMayoristas']
    mayorista = False
    precioBase = prod['precioBase']
    descuento = 0
    for i in range(0, len(predMayo)):
        for j in range(0, len(predMayo)-1):
            if predMayo[j]['cantidad']>predMayo[j+1]['cantidad']:
                aux = predMayo[j]
                predMayo[j] = predMayo[j+1]
                predMayo[j+1] = aux
    
    for x in predMayo:
        if detalle.cantidad >= x['cantidad'] :
            mayorista = True
            pMayorista = x['precio']
    
    if metCal==1:
        subTotal = (detalle.cantidad * precioBase) #+ delivery
        total = subTotal
        if(mayorista==True):
            total = (detalle.cantidad * pMayorista) #+ delivery
            descuento = subTotal-total
    elif metCal==2 or metCal==3:
        dm2 = detalle.medidas.ancho * detalle.medidas.alto
        precioBase = dm2 * precioBase
        subTotal = (precioBase * detalle.cantidad) #+ delivery
        total = subTotal
        if mayorista == True:
            total = (dm2 * pMayorista * detalle.cantidad) #+ delivery
            descuento = subTotal-total
    #rutas de archivos se van a agregar desde upload
    seq = db['seqDet'].find_one_and_update({"codPedido": detalle.codPedido}, {"$inc":{"seq": 1}}, upsert = True, return_document=ReturnDocument.AFTER)
    codDetalle = str(detalle.codPedido) + "-" + str(seq['seq'])
    datos = {
        'codDetalle': codDetalle,
        'codPedido': detalle.codPedido,
        'precioU': precioBase,
        'cantidad': detalle.cantidad,
        'subTotal': subTotal,
        'descuento': descuento,
        'presupuesto': total,
        'descripcion': detalle.descripcion,
        'fechaEntrega': detalle.fechaEntrega,
        'detalleProducto': {
            'codProducto': detalle.codProducto,
            'metodoCalculo': prod['metodoCalculo'],
            'medidas': json.loads(detalle.medidas.json())
        },
        'entrega': {
            'entregado': False
        }#,
        #'inforDelivery': {
         #   'solicitado': detalle.delivery.solicitado,
          #  'costoDelivery': delivery,
           # 'direccion': detalle.delivery.direccion
        #}
    }
    db['detallesPedidos'].insert_one(json_util._json_convert(datos))
    idCliente = json_util._json_convert(db['pedidos'].find_one({'codPedido': detalle.codPedido}))['cliente_id']['$oid']
    print(idCliente)
    db['clientes'].update_one({'_id': ObjectId(idCliente)}, {"$inc": {'saldo': total}})
    db['cuentas'].find_one_and_update({"codPedido": detalle.codPedido, "cliente_id": ObjectId(idCliente)}, {"$inc":{"total": total, "saldo": total}}, upsert = True)
    actPresu = models.actPresu(codPedido=detalle.codPedido, subTotal=subTotal, descuento=descuento, total=total, presupuesto=total)
    actPresuPedido(pedido=actPresu)

    montoSena = find_one('configuraciones')
    totalActual = find_one('pedidos', {'codPedido': detalle.codPedido})
    #print(totalActual['presupuesto'])
    #inserta o no a produccion dependiendo si alcanza o no el monto minimo requerido para seña
    senaRequired = False
    if totalActual['presupuesto'] < montoSena['senas']['monto']:
        """db['produccion'].insert_one({
            "codProduccion": codDetalle,
            "detallesPedidos_id": ObjectId(find_one('detallesPedidos', {'codDetalle': codDetalle})['_id']),
            "cantidadRestante": detalle.cantidad,
            "etapa":{
                'codEtapa': 0,
                'descripcion': "No Iniciado"
            }
        })"""
        trabajos.pasarAProduccion(codDetalle)
        
    else:
        """detalles = find('detallesPedidos', {'codPedido': detalle.codPedido})
        for i in detalles:
            if find_one('produccion', {'detallesPedidos_id': ObjectId(i['_id'])}) == None:
                break
            await delete_one('produccion', {'detallesPedidos_id': ObjectId(i['_id'])})"""
        await trabajos.deleteAllOfProduccion(detalle.codPedido)
        senaRequired = True
    presupuestoTotal = db['pedidos'].find_one({'codPedido': detalle.codPedido})['presupuesto']
    return {'msg': 'success', 'codDetalle': codDetalle, 'presupuesto': total, 'total': presupuestoTotal , 'SenaRequerida': senaRequired}

@Pedidos.delete("/eliminar_det")
async def eliminarDet(response: Response, codDetalle : str, user=Depends(manager)):
    codPedido = json_util._json_convert(db['detallesPedidos'].find_one({'codDetalle': codDetalle}))
    produccion = db['produccion'].find_one({'detallesPedidos_id': ObjectId(codPedido['_id']['$oid'])})
    if produccion != None:
        if produccion['etapa']['codEtapa'] != 0 and produccion['etapa']['codEtapa'] != 3:
            response.status_code = status.HTTP_409_CONFLICT
            return {'msg': 'No se puede eliminar, la producción está en proceso o ya fue terminado'}
    codPedido = codPedido['codPedido']
    anterior = db['detallesPedidos'].find_one({'codDetalle': codDetalle})
    usuario_id = db['usuarios'].find_one({'username': user.username})
    datosAuditoria = {
        'codDetalle': codDetalle,
        'fecha': datetime.datetime.now().strftime("%y-%m-%d %H:%M"),
        'usuario': usuario_id['_id'],
        'accion': 'eliminar',
        'anterior': anterior
    }
    db['auditoriaDetallesPedidos'].insert_one(datosAuditoria)
    db['detallesPedidos'].delete_one({'codDetalle': codDetalle})
    result = infoPedidos.actPresupuesto(codPedido)
    newDatos = db['pedidos'].find_one({'codPedido': codPedido})
    return {'msg':'success',
    'presupuesto': newDatos['presupuesto'],
    'vuelto': result['vuelto'],
    'saldo': result['saldo'],
    'numeroRecibo': result['numeroRecibo']
    }

@Pedidos.delete("/eliminar_pedido", status_code=status.HTTP_200_OK)
async def eliminarPedido(resonse: Response, codPedido: str, user=Depends(manager)):
    try:
        await infoPedidos.eliminarPedido(codPedido=codPedido)
        return {'msg':'success'}
    except Exception as e:
        print(e)
        resonse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    
@Pedidos.get('/resumen/{cod}')
async def resumenPedido(request: Request, cod: str, user=Depends(manager)):
    pedido = infoPedidos.infoDetalle(cod)
    delivery = infoPedidos.infoPedido(cod)['infoDelivery']
    fecha =  infoPedidos.infoPedido(cod)['fecha']
    cliente = infoPedidos.infoCliente(cod)

    return templates.TemplateResponse('base_res_pedido.html', context={'request': request, 'cliente': cliente , 'pedido': pedido, 'delivery': delivery, 'codPedido': cod, 'fecha': fecha})


@Pedidos.get('/info_detalle')
async def infoDetallePedido(response: Response, codDetalle:str, user=Depends(manager)):
    detalle = infoPedidos.infoOneDetalle(codDetalle)
    return json_util._json_convert(detalle)

@Pedidos.post('/editar_detalle')
async def editarDetalle(response: Response, datos:models.editarDet, user=Depends(manager)):
    _id = db['detallesPedidos'].find_one({'codDetalle': datos.codDetalle})['_id']
    produccion = db['produccion'].find_one({'detallesPedidos_id': _id})
    if(produccion != None and produccion['etapa']['codEtapa'] != 0):
        response.status_code = status.HTTP_409_CONFLICT
        return {'msg': 'Producción iniciado, no se puede editar el pedido'}
    anterior = db['detallesPedidos'].find_one({'codDetalle': datos.codDetalle, 'codPedido': datos.codPedido})
    if anterior == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None
    actual = json.loads(datos.json())
    usuario_id = db['usuarios'].find_one({'username': user.username})
    datosAuditoria = {
        'codDetalle': datos.codDetalle,
        'fecha': datetime.datetime.now().strftime("%y-%m-%d %H:%M"),
        'usuario': usuario_id['_id'],
        'accion': 'editar',
        'anterior': anterior,
        'cambios': actual
    }
    db['auditoriaDetallesPedidos'].insert_one(datosAuditoria)

    prod = db['productos'].find_one({'codProducto': anterior['detalleProducto']['codProducto']})
    metCal = prod['metodoCalculo']['codMetodo']
    predMayo = prod['preciosMayoristas']
    mayorista = False
    precioBase = prod['precioBase']
    descuento = 0
    for i in range(0, len(predMayo)):
        for j in range(0, len(predMayo)-1):
            if predMayo[j]['cantidad']>predMayo[j+1]['cantidad']:
                aux = predMayo[j]
                predMayo[j] = predMayo[j+1]
                predMayo[j+1] = aux
    
    for x in predMayo:
        if datos.cantidad > x['cantidad'] :
            mayorista = True
            pMayorista = x['precio']
    
    if metCal==1:
        subTotal = (datos.cantidad * precioBase) #+ delivery
        total = subTotal
        if(mayorista==True):
            total = (datos.cantidad * pMayorista) #+ delivery
            descuento = subTotal-total
    elif metCal==2 or metCal==3:
        dm2 = datos.medidas.ancho * datos.medidas.alto
        precioBase = dm2 * precioBase
        subTotal = (precioBase * datos.cantidad) #+ delivery
        total = subTotal
        if mayorista == True:
            total = (dm2 * pMayorista * datos.cantidad) #+ delivery
            descuento = subTotal-total

    presupuesto = {
        'subTotal': subTotal,
        'descuento': descuento,
        'presupuesto': total
    }
    if anterior['cantidad'] != datos.cantidad:
        incCant = datos.cantidad - anterior['cantidad']
        db['produccion'].update_one({'detallesPedidos_id': _id}, {'$inc': {'cantidadRestante': incCant}})
    
    db['detallesPedidos'].update_one({'codDetalle': datos.codDetalle, 'codPedido': datos.codPedido}, {'$set': json.loads(datos.json())})
    
    if anterior['presupuesto'] != presupuesto['presupuesto'] or anterior['descuento'] != presupuesto['descuento'] or anterior['subTotal'] != presupuesto['subTotal']:
        db['detallesPedidos'].update_one({'codDetalle': datos.codDetalle, 'codPedido': datos.codPedido}, {'$set': presupuesto })
        infoPedidos.actPresupuesto(datos.codPedido)
    return json_util._json_convert(presupuesto)

@Pedidos.post('/actualizar_info')
async def actualizarDelivery(response: Response, codPedido: str ,datos: models.actInfoPedido, user=Depends(manager)):
    
    if (datos.delivery.direccion == '' and datos.delivery.solicitado == True):
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return 0
    anterior = db['pedidos'].find_one({'codPedido': codPedido})
    if anterior == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None
    actual = json.loads(datos.json())
    infoDelivery = anterior['infoDelivery']
    infoFechaEntrega = db['detallesPedidos'].find_one({'codPedido': codPedido})
    infoFechaEntrega = infoFechaEntrega['fechaEntrega']
    actual['delivery']['costoDelivery'] =  infoDelivery['costoDelivery']
    anterior['fechaEntrega'] = infoFechaEntrega
    if infoDelivery['costoDelivery'] <= 0 and datos.delivery.solicitado == True:
        costoDelivery = db['configuraciones'].find_one()['delivery']['costoDelivery']
        actual['delivery']['costoDelivery'] = costoDelivery
    usuario_id = db['usuarios'].find_one({'username': user.username})
    datosAuditoria = {
        'codPedido': codPedido,
        'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'usuario': usuario_id['_id'],
        'accion': 'editar',
        'anterior': anterior,
        'cambios': actual
    }
    db['auditoriaPedidos'].insert_one(datosAuditoria)
    if datos.delivery.solicitado != infoDelivery['solicitado']:
        db['pedidos'].update_one({'codPedido': codPedido}, {'$set':{'infoDelivery':actual['delivery']}})
        infoPedidos.actPresupuesto(codPedido)
    if datos.fechaEntrega != infoFechaEntrega:
        db['detallesPedidos'].update_many({'codPedido': codPedido}, {'$set': {'fechaEntrega': datos.fechaEntrega}})
    
    newPresu = db['pedidos'].find_one({'codPedido': codPedido})
    newSaldo = db['cuentas'].find_one({'codPedido': codPedido})
    return {'msg': 'success',
    'saldo': newSaldo['saldo'],
    'presupuesto': newPresu['presupuesto']}

@Pedidos.post('/entregar_detalle')
async def entregarDetalle(response: Response, datos: models.entregarDetalle, user=Depends(manager)):
    _id = db['detallesPedidos'].find_one({'codDetalle': datos.codDetalle})
    _id = _id['_id']
    estado = db['produccion'].find_one({'detallesPedidos_id': _id})['etapa']
    if estado['codEtapa'] == 2:
        entrega = {
            'fechaEntrega': datos.fechaEntrega,
            'entregado': datos.entregado
        }
        db['detallesPedidos'].update_one({'codDetalle': datos.codDetalle}, {'$set': {'entrega': entrega}})
        return {'msg': 'success'}
    response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return {'msg': 'Producción sin terminar, no se puede entregar'}

@Pedidos.post('/entregar_pedido')
async def entregarDetalle(response: Response, datos: models.entregarPedido, user=Depends(manager)):
    estado = trabajos.estadoProduccionPedido(datos.codPedido)
    if estado['produccionTerminada'] == True:
        entrega = {
            'fechaEntrega': datos.fechaEntrega,
            'entregado': datos.entregado
        }
        db['detallesPedidos'].update_many({'codPedido': datos.codPedido}, {'$set': {'entrega': entrega}})
        return {'msg': 'success'}
    response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return {'msg': 'Producción sin terminar, no se puede entregar'}


