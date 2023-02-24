from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from fastapi import status
from fastapi import Depends
from fastapi.responses import FileResponse
from nlt import numlet as nl
from bson import json_util, ObjectId
from models import pagos, factura
from pymongo import MongoClient, ReturnDocument
from manager import	 manager
from functions import infoPedidos, trabajos
from config import settings


from jinja2 import Environment
from jinja2 import FileSystemLoader
from pdfkit import from_string

from fastapi import Response, BackgroundTasks

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]
Pagos = APIRouter()
templates = Jinja2Templates(directory="templates")

@Pagos.get("/cobranza")
async def Cobranza(request: Request, documento: str = '', codPedido:str='', user = Depends(manager)):
    return templates.TemplateResponse('cobranza.html', context={'request': request, 'documento': documento, 'codPedido': codPedido, 'userInfo': user})

@Pagos.post("/registrar_pago")
async def registrarPago(response: Response, datos: pagos, user = Depends(manager)):
    if datos.monto <= 0:
        response.status_code = status.HTTP_402_PAYMENT_REQUIRED
        return None
    print(datos)
    if datos.monto <= 0:
        response.status_code = status.HTTP_402_PAYMENT_REQUIRED
        return {'msg': "Pago Requerido"}
    seq = db['seq'].find_one_and_update({"cod": 2}, {"$inc":{"seq": 1}}, upsert=True , return_document=ReturnDocument.AFTER)
    numRecibo = '0'*(settings.NUM_RECIBO - len(str(seq['seq']))) + str(seq["seq"])
    infoPedido = infoPedidos.infoPedido(datos.codPedido)
    saldo = db['cuentas'].find_one({'codPedido': datos.codPedido, 'cliente_id': ObjectId(datos.cliente_id)})
    saldo = saldo['saldo']
    upd = {
        '$inc':{
            "saldo": -datos.monto
        },
        "$push": {"pagos": {
            "fecha": datos.fecha,
            "monto": datos.monto,
            "saldo": saldo - datos.monto,
            "numeroRecibo": numRecibo
            }
        }
    }

    if datos.monto >= (infoPedido['presupuesto']/2):
        trabajos.pasarTodoAProduccion(datos.codPedido)

    pago = db['cuentas'].find_one_and_update({'codPedido': datos.codPedido, 'cliente_id': ObjectId(datos.cliente_id)}, upd, upsert=True, return_document=ReturnDocument.AFTER)
    db['clientes'].update_one({'_id': ObjectId(datos.cliente_id)}, {'$inc': {'saldo': -datos.monto}})
    return {"saldo": pago['saldo'],
            "total": pago['total'],
            "numeroRecibo": numRecibo
            }

@Pagos.post("/generar_factura")
async def generarFactura(response: Response, datos: factura, user = Depends(manager)):
    print(datos)
    pagoContado = False
    subTotal = 0
    descuento = 0
    total = 0
    infoCliente = json_util._json_convert(db['clientes'].find_one({'_id': ObjectId(datos.cliente_id)}))
    seq = db['seq'].find_one_and_update({"cod": 3}, {"$inc":{"seq": 1}}, upsert=True , return_document=ReturnDocument.AFTER)
    numFactura = '0'*(settings.NUM_FACTURA - len(str(seq['seq']))) + str(seq["seq"])
    datosFactura = {
            "numeroFactura": numFactura,
            "fecha": datos.fecha,
            "iva": 0,
            "total": 0,
            "detalleFactura": [
            ],
            "cliente_id": ObjectId(infoCliente['_id']['$oid'])

    }
    print(datosFactura['detalleFactura'])
    for codPedido in datos.codPedido:
        pago = db['cuentas'].find_one({'codPedido': codPedido})

        if pago['saldo'] > 0:
            response.status_code = status.HTTP_402_PAYMENT_REQUIRED
            return None
        if(len(pago['pagos']) == 1):
                pagoContado = True
                break
    for codPedido in datos.codPedido:
        detalleFactura = {
            "codPedido": codPedido,
            "detalles": []
        }
        print(datosFactura['detalleFactura'])
        detallePedido = infoPedidos.infoDetalle(codPedido)
        for i in detallePedido:
            detalle = {
                "cantidad": i['pedido']['cantidad'],
                "descripcionProducto": i['producto']['descripcion'],
                "precioUnitario": i['pedido']['precioU'],
                "descuento": i['pedido']['descuento'],
                "subtotal": i['pedido']['subTotal'],
                "total": i['pedido']['presupuesto']
            }
            subTotal = subTotal + detalle['subtotal']
            total = total + detalle['total']
            descuento = descuento + detalle['descuento']
            detalleFactura['detalles'].append(detalle)
        delivery = infoPedidos.infoPedido(codPedido)['infoDelivery']
        if delivery['solicitado'] == True:
            detalleDelivery = {
                "cantidad": 1,
                "descripcionProducto": "Servicio de delivery",
                "precioUnitario": delivery['costoDelivery'],
                "descuento": 0,
                "subtotal": delivery['costoDelivery'],
                "total": delivery['costoDelivery']
            }
            subTotal = subTotal + delivery['costoDelivery']
            total = total + delivery['costoDelivery']
            detalleFactura['detalles'].append(detalleDelivery)
        datosFactura['detalleFactura'].append(detalleFactura)
    datosFactura["subtotal"]= subTotal 
    datosFactura["descuento"] = descuento
    datosFactura['iva'] =  int((subTotal-descuento)/11),
    datosFactura["total"] = total,
    datosFactura["ventaContado"] = pagoContado 
    datosFactura['iva'] = datosFactura["iva"][0]
    datosFactura["total"] = datosFactura["total"][0]
    db['facturas'].insert_one(datosFactura)
    return {'numeroFactura': numFactura}

@Pagos.get("/imprimir_factura/{num}")
def imprimirRecibo(request: Request, background_tasks: BackgroundTasks, num:str, user=Depends(manager)):
    datosFactura = db['facturas'].find_one({'numeroFactura': num})
    infoCliente = db['clientes'].find_one({'_id': ObjectId(datosFactura['cliente_id'])})
    options = {
        'page-size': 'a4',
        'margin-top': '0.35in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        #'footer-right': 'Página [page] de [topage]',
        #'orientation': 'Landscape'
        
    }
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('base_factura.html')
    html_out = template.render(datosFactura, cliente = infoCliente)
    file_content = from_string(
        html_out,
        False,
        options=options,
        #options='here_a_dict_with_special_page_properties',
        css=['assets/vendor/bootstrap/css/bootstrap.min.css', "assets/css/style.css"] # its a list e.g ['my_css.css', 'my_other_css.css']
    )
    #background_tasks.add_task(file_content)
    headers = {'Content-Disposition': 'inline; filename="recibo - ' + datosFactura['numeroFactura'] +'".pdf"'}
    return Response(file_content, headers=headers, media_type='application/pdf')

@Pagos.get("/imprimir_recibo/{num}")
def imprimirRecibo(request: Request, background_tasks: BackgroundTasks, num:str, user=Depends(manager)):    
    recibo = db['cuentas'].find_one({'pagos.numeroRecibo': num})
    concepto = "Pago por pedido Número "+ recibo['codPedido']
    
    cliente = db['clientes'].find_one({'_id': ObjectId(recibo['cliente_id'])})
    for i in  recibo['pagos']:
        if i['numeroRecibo'] == num:
            datos = i
            monto = nl.Numero(i['monto']).a_letras.upper()
            break
    template_vars = {
        "cliente": cliente, 
        "recibo": datos, 
        "monto": monto, 
        "concepto": concepto
        }
    options = {
        'page-size': 'a4',
        'margin-top': '0.35in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        #'orientation': 'Landscape'
        
    }

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('base_recibo.html')
    html_out = template.render(template_vars)
    
    file_content = from_string(
        html_out,
        False,
        options=options,
        #options='here_a_dict_with_special_page_properties',
        css=['assets/vendor/bootstrap/css/bootstrap.min.css', "assets/css/style.css"] # its a list e.g ['my_css.css', 'my_other_css.css']
    )
    #background_tasks.add_task(file_content)
    headers = {'Content-Disposition': 'inline; filename="recibo - ' + datos['numeroRecibo'] +'".pdf"'}
    return Response(file_content, headers=headers, media_type='application/pdf')

#estado de la cuenta de un grupo de pedido
@Pagos.get("/info_cuenta")
async def estadoCuenta(response: Response, codPedido:str, user=Depends(manager)):
    datos = db['cuentas'].find_one({'codPedido': codPedido})
    estadoProduccion = trabajos.estadoProduccionPedido(codPedido)
    entregados = infoPedidos.estadoEntrega(codPedido)
    datos['estadoProduccion'] = estadoProduccion
    datos['entregados'] = entregados
    return json_util._json_convert(datos)
