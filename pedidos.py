from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from bson import json_util, ObjectId
import models
from pymongo import MongoClient, errors, ReturnDocument
import datetime
import json
client = MongoClient("localhost")
db = client['cym']
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
async def pedidos(request: Request):
    return templates.TemplateResponse("pedidos.html", context={"request": request})

@Pedidos.get('/nuevo_pedido')
async def nuevo_pedido(request: Request):
    productos =json_util._json_convert(db['productos'].find())
    #print(json_util.dumps(productos))
    delivery = json_util._json_convert(db['delivery'].find_one())
    return templates.TemplateResponse('cym_nuevo_pedido.html', context={'request': request, 'productos': productos, 'delivery' : delivery})    


@Pedidos.post('/create_pedido', status_code=status.HTTP_201_CREATED)
async def createPedido(pedido: models.basePedido, response: Response):
    date = datetime.datetime.now().strftime("%y%m")
    try:
        seq = db['seq'].find_one_and_update({"date": date}, {"$inc":{"seq": 1}}, upsert = True, return_document=ReturnDocument.AFTER)
    except errors.ConnectionFailure as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': e}
    codPedido = "PE"+str(date)+str(seq['seq'])
    data = {
        "codPedido": codPedido,
        "fecha": pedido.fecha,
        "cliente_id": ObjectId(pedido.cliente_id)
    }
    try:
        db['pedidos'].insert_one(data)
    except errors.ConnectionFailure as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': e}
    return {'msg' : "success",
    "codPedido": codPedido
    }


@Pedidos.post('/agg_detpedido', status_code=status.HTTP_201_CREATED)
async def aggDetPedido(response: Response, detalle:models.detPedido):
    prod = db['productos'].find_one({'codProducto': detalle.codProducto})
    metCal = prod['metodoCalculo']['codMetodo']
    predMayo = prod['preciosMayoristas']
    mayorista = False
    precioBase = prod['precioBase']
    delivery = 0
    descuento = 0
    #print(predMayo)
    if detalle.delivery == True:
        delivery = db['delivery'].find_one()['precioDelivery']

    for i in range(0, len(predMayo)):
        for j in range(0, len(predMayo)-1):
            if predMayo[j]['cantidad']>predMayo[j+1]['cantidad']:
                aux = predMayo[j]
                predMayo[j] = predMayo[j+1]
                predMayo[j+1] = aux
    
    for x in predMayo:
        if detalle.cantidad > x['cantidad'] :
            mayorista = True
            pMayorista = x['precio']
    
    if metCal==1:
        subTotal = (detalle.cantidad * precioBase) + delivery
        total = subTotal
        if(mayorista==True):
          total = (detalle.cantidad * pMayorista) + delivery
          descuento = subTotal-total

    elif metCal==2 or metCal==3:
        dm2 = detalle.medidas.ancho * detalle.medidas.alto
        subTotal = (dm2 * precioBase * detalle.cantidad) + delivery
        total = subTotal
        if mayorista == True:
            total = (dm2 * pMayorista * detalle.cantidad) + delivery
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
        },
        'inforDelivery': {
            'solicitado': detalle.delivery,
            'costoDelivery': delivery
        }
    }
    db['detallesPedidos'].insert_one(json_util._json_convert(datos))
    db['produccion'].insert_one({
        "codDetalle": codDetalle,
        "cantidadRestante": detalle.cantidad,
        "etapa":{
            'codEtapa': 0,
            'descripcion': "No Iniciado"
        }
    })
    actPresu = models.actPresu(codPedido=detalle.codPedido, subTotal=subTotal, descuento=descuento, total=total, presupuesto=total)
    actPresuPedido(pedido=actPresu)
    return {'msg': 'success', 'codDetalle': codDetalle, 'presupuesto': total}

@Pedidos.delete("/eliminar_det")
async def eliminarDet(codDetalle : str):
    db['detallesPedidos'].delete_one({'codDetalle': codDetalle})

    return 'success'
