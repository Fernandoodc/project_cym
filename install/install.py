from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017')
#nombre de la base de datos
dbName = 'c_y_m'
db = client[dbName]

print('Bienvenido al asistente de instalación del sistema CYM\t')
print('1: Configurar BD. Esta opción pronda en condiciones la base de datos del sistema,\t')
print('si ya existe una base de datos anterior la eliminará')
print('2: Restablecer usuario de acceso. Elinará todos los usuarios del sistema y\trestablecerá el usuario por defeccto')
opc = int(input('opcion: '))
if opc == 1:
    client.drop_database(dbName)
    #colecciones para crear los index
    colecciones = {
        'pedidos': 'codPedido',
        'detallesPedidos': 'codDetalle',
        'produccion': 'codProduccion',
        'facturas': 'numeroFactura',
        'productos': 'codProducto',
        'insumos': 'codInsumo',
        'usuarios': 'username'
    }
    print("creando Index's")
    for i in colecciones:
        db[i].create_index(colecciones[i], unique=True)
        print(i+' - listo')
    #archivos obligatorios en la bd
    print('Index Creados')
    print('Agregando datos obligatorios')
    archivos =  ['configuraciones', 'etapasProduccion', 'nacionalidades', 'tiposInsumos', 'tiposUsuarios', 'usuarios']
    for i in archivos:
        with open('datos/'+i+'.json') as f:
            db[i].insert_many(json.load(f))
            print(i+' - listo')
    print('Base de Datos configurada')
elif opc == 2:
    db.drop_collection('usuarios')
    with open('datos/usuarios.json') as f:
            db['usuarios'].insert_many(json.load(f))
    print('usuario de acceso restablecido')
    print('user = adminpassword = admin')


