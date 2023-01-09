function get_client() {
    doc = document.getElementById('documento').value
        $.ajax({
            type: "GET",
            url: "/clientes/get_client/?doc="+doc,
            
            success: function(result, textStatus, xhr) { 
               console.log(result)
                if(xhr.status == 200){
                    console.log(xhr.status)
                    id_cliente = result._id.$oid
                    document.getElementById('nombre').value=result.nombre + " " + result.apellido
                    document.getElementById('numCelular').value = result.celular
                    document.getElementById('direccion').value = result.direccion
                    $('#alertText').html('')
                }
            },
            complete: function(xhr, textStatus) {
                console.log(xhr.status)
                if(xhr.status == 404){
                    id_cliente = null
                    document.getElementById('nombre').value= ""
                    document.getElementById('numCelular').value = ""
                    document.getElementById('direccion').value = ""
                    $('#alertText').html('cliente no encontrado')
                }
                else
                    if(xhr.status==401){
                        unauthorized()
                    }
            } 
        });
    
}

async function create_pedido(data){
    console.log("desde create_pedido" + data)
    await $.ajax({
        type: "POST",
        url: "/pedidos/create_pedido",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result.codPedido)
            codPedido = result.codPedido

        },
        complete: function(xhr, textStatus){
            console.log(textStatus)
            if(xhr.status != 201){
                codPedido = 0;
            }
            return 0
        } 
    });
    return codPedido

}

 
async function aggDetallePedido(data){
    let response = {
    }
    await $.ajax({
        type: "POST",
        url: "/pedidos/agg_detpedido",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            response.codDetalle = result.codDetalle
            response.presu = result.presupuesto

        },
        complete: function(xhr, textStatus){
            console.log(textStatus)
            if(xhr.status != 201){
                response = 0;
            }
        }
    });
    return response
}

async function uploadFiles(data){
    let rutas = []
    await $.ajax({
        type: "POST",
        enctype: 'multipart/form-data',
        url: "/upload",
        data: data,
        processData: false,
        contentType: false,
        cache: false,
        //timeout: 600000,
        success: function (data) {

            //$("#result").text(data);
            console.log("SUCCESS : ", data.files);
            rutas = data.files;
           //$("#btnSubmit").prop("disabled", false);

        },
        error: function (e) {
            //$("#result").text(e.responseText);
            console.log("ERROR : ", e);
            rutas = 0 ;
            //$("#btnSubmit").prop("disabled", false);

        }
    });
    return rutas;
}

function eliminarDet(codDet){
    $.ajax({
        type: "DELETE",
        url: "/pedidos/eliminar_det?codDetalle="+codDet,
        success: function(result, textStatus, xhr) { 
            console.log(result)
            document.getElementById(codDet).remove()

        },
        complete: function(xhr, textStatus) {
        } 
    });
}

async function eliminarPedido(codPedido){
    $.ajax({
        type: "DELETE",
        url: "/pedidos/eliminar_pedido?codPedido="+codPedido,
        success: function(result, textStatus, xhr) { 
            
        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e.responseText)
            alert(e)
        }
    });
}

function get_products(){
        $.ajax({
            type: "GET",
            url: "/get_client/?doc="+doc,
            
            success: function(result, textStatus, xhr) { 
                console.log(result)
                document.getElementById('nombre').value=result.nombre + " " + result.apellido
                document.getElementById('numCelular').value = result.celular
                document.getElementById('direccion').value = result.direccion

            },
            complete: function(xhr, textStatus) {
            } 
        });
    
}

async function infoProduccion(codProduccion){
    let response = {}
    await $.ajax({
        type: "GET",
        url: "/trabajos/info_produccion/" + codProduccion,        
        success: function(result, textStatus, xhr) { 
            response = result

        },
        complete: function(xhr, textStatus) {
        } 
    });
    return response

}

function viewFile(codPedido, codDet, filename){
    $.ajax({
        type: "GET",
        url: "/info_produccion/" + codProduccion,        
        success: function(result, textStatus, xhr) { 
            response = result

        },
        complete: function(xhr, textStatus) {
        } 
    });
    return response
}

async function uploaDesign(desing){
    let rutas = []
    await $.ajax({
        type: "POST",
        enctype: 'multipart/form-data',
        url: "/upload_diseno",
        data: desing,
        processData: false,
        contentType: false,
        cache: false,
        //timeout: 600000,
        success: function (data) {
            //$("#result").text(data);
            console.log("SUCCESS : ", data.files);
            rutas = data.files;
           //$("#btnSubmit").prop("disabled", false);

        },
        error: function (e) {
            //$("#result").text(e.responseText);
            console.log("ERROR : ", e.responseText);
            rutas = 0 ;
            //$("#btnSubmit").prop("disabled", false);

        }
    });
    return rutas;
}

async function deleteDesing(codPedido, codDetalle, codProduccion, filename){
    $.ajax({
        type: "DELETE",
        url: "/delete_disenio?"+ $.param({"filename": filename, "cod_pedido" : codPedido, "cod_produccion": codProduccion, "cod_detalle": codDetalle}),
        success: function(result, textStatus, xhr) { 
            
        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e.responseText)
            alert(e)
        }
    });
}

async function aprovacion(data){
    await $.ajax({
        type: "POST",
        url: "/trabajos/act_aprovacion",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
        

        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
        }
    });
}

async function agregarProveedor(datos){
    var response
    await $.ajax({
        type: "POST",
        url: "/proveedores/agregar_proveedor",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            
        },
        complete: function(xhr, textStatus){
            if(xhr.status == 409){
                response = xhr.status
            }
        },
        error: function(e){
            console.log(e.statusText)
            console.log(e)
        }
    });
    return response

}

async function listaFacturas(proveedor){
    var response
    await $.ajax({
        type: "GET",
        url: "/proveedores/"+ proveedor +"/facturas",
        success: function(result, textStatus, xhr) { 
            response = result
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
        }
    });
    return response
}

async function agregarFactura(datos){
    var response = 0
    await $.ajax({
        type: "POST",
        url: "/proveedores/facturas/agregar_factura",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            
        },
        complete: function(xhr, textStatus){
            response = xhr.status
        },
        error: function(e){
            console.log(e.status)
            console.log(e)
            response = e.status
            if(e.status == 409){
                $('#alertNuevaFactura').addClass('alert-danger')
                $('#alertNuevaFactura').html('La factura ya existe')
            }
            if(e.status == 500){
                $('#alertNuevaFactura').addClass('alert-warning')
                $('#alertNuevaFactura').html('Ocurrió un error interno')
            }
        }
    });
    return response;
}
async function agregarInsumo(datos){
    var response
    await $.ajax({
        type: "POST",
        url: "/insumos/nuevo_insumo",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result)
            response = result
        },
        complete: function(xhr, textStatus){
            //response = xhr.status
        },
        error: function(e){
            console.log(e.status)
            console.log(e)
        }
    });
    return response;
}

async function registrarCompra(datos){
    var response
    await $.ajax({
        type: "POST",
        url: "/insumos/compra_insumos",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result)
            response = result
        },
        complete: function(xhr, textStatus){
            //response = xhr.status
        },
        error: function(e){
            console.log(e.status)
            console.log(e)
        }
    });
    return response;
}

async function eliminarCompraAjax(id){
    $.ajax({
        type: "DELETE",
        url: "/insumos/compra_insumos/eliminar_compra?"+ $.param({"idCompra": id}),
        success: function(result, textStatus, xhr) { 
            
        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e.responseText)
            alert(e)
        }
    });
}