async function infoCliente(doc) {
        response = null
        await $.ajax({
            type: "GET",
            url: "/clientes/get_client/?doc="+doc,
            
            success: function(result, textStatus, xhr) { 
                response = result
            },
            complete: function(xhr, textStatus) {
            },
            error: function(e){
                console.log(e)
            }
        });
        return response
    
}

async function editarCliente(datos, cliente_id){
    response = null
    await $.ajax({
        type: "PUT",
        url: "/clientes/editar_cliente?"+$.param({'cliente_id': cliente_id}),
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            response = result
        },
        complete: function(xhr, textStatus){
            $('#guardar').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
    return response

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
            response.senaRequerida = result.SenaRequerida
            response.total = result.total

        },
        complete: function(xhr, textStatus){
            console.log(textStatus)
            if(xhr.status != 201){
                response = 0;
            }
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
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
            $("#aggArchivo").prop("disabled", false)
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
            window.location.reload()
        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e.responseText)
            alert(e)
        }
    });
}

function actInfoPedido(codPedido, datos){
    $.ajax({
        type: "POST",
        url: "/pedidos/actualizar_info?"+$.param({'codPedido': codPedido}),
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result)
            $('#saveChange-btn').prop('hidden', true)
            $('.changeInfo').prop('hidden', true)
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
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

async function detallesPedido(codDetalle){
    var response 
    await $.ajax({
        type: "GET",
        url: "/pedidos/info_detalle?codDetalle="+codDetalle,
        
        success: function(result, textStatus, xhr) { 
            response = result
            console.log(result)

        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
    return response
}

async function editarDetalle(datos){
    var response
    await $.ajax({
        type: "POST",
        url: "/pedidos/editar_detalle",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            response = result
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
            //alert(e.statusText)
            if(e.status == 409){
                $('#alertPedidos').prop('hidden', false)
                $('#alertPedidos-span').text('La producción ya inició, no se puede editar el producto')
            }
        }
    });
    return response;
}

async function entregarDetalle(codDetalle){
    var check = $('#check-'+codDetalle)
    datos = {
        codDetalle: codDetalle,
        entregado: check.is(':checked')
    }
    await $.ajax({
        type: "POST",
        url: "/pedidos/entregar_detalle",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            response = result
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
            alert(e.responseJSON.msg)
            check.prop('checked', !check.is(':checked'))
            
        }
    });
}

async function entregarPedido(datos){
    await $.ajax({
        type: "POST",
        url: "/pedidos/entregar_pedido",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            $('.entregar-btn').hide()
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
            alert(e.responseJSON.msg)
            $('#entregarPedido-btn').prop('disabled', false)
            
        }
    });
}

async function estadoProduccion(codPedido){
    let response = {}
    await $.ajax({
        type: "GET",
        url: "/trabajos/estado_produccion?" + $.param({'codPedido': codPedido}),        
        success: function(result, textStatus, xhr) { 
            response = result

        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e)            
        }
    });
    return response
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
async function deleteArchivo(filename, codPedido, codDetalle){
    $.ajax({
        type: "DELETE",
        url: "/delete_archivo?"+ $.param({"filename": filename, "cod_pedido" : codPedido, "cod_detalle": codDetalle}),
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
    var response
    $.ajax({
        type: "DELETE",
        url: "/insumos/compra_insumos/eliminar_compra?"+ $.param({"idCompra": id}),
        success: function(result, textStatus, xhr) { 
            response = true
        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            response = false
            console.log(e.responseText)
            alert(e.responseText)
        }
    });
    return response
}

async function enviarTerminados(datos){
    var response
    await $.ajax({
        type: "POST",
        url: "/trabajos/produccion/procesar",
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
            console.log(e.textStatus)
            alert(e.statusText)
            $('#guardarTerminados').prop('disabled', false)
        }
    });
    return response;
}
async function cancelarProduccion(codProduccion){
    $.ajax({
        type: "PUT",
        url: "/trabajos/produccion/cancelar?"+ $.param({"codProduccion": codProduccion}),
        success: function(result, textStatus, xhr) { 
        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e.responseText)
            alert(e.responseText)
            $('#cancelarProduccion').prop('disabled', false)
        }
    });
}
async function pausarProduccion(codProduccion){
    $.ajax({
        type: "PUT",
        url: "/trabajos/produccion/pausar?"+ $.param({"codProduccion": codProduccion}),
        success: function(result, textStatus, xhr) { 
        },
        complete: function(xhr, textStatus) {
        },
        error: function(e){
            console.log(e.responseText)
            alert(e.responseText)
            $('#cancelarProduccion').prop('disabled', false)
        }
    });
}

async function solicitarInsumos(datos){
    return await $.ajax({
        type: "POST",
        url: "/trabajos/produccion/solicitar_insumos",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result)
            return result
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
            $('#solicitarInsumo').prop('disabled', false)
        }
    });
}

async function tipoInsumo(codInsumo){
    return await $.ajax({
        type: "GET",
        url: "/insumos/infoInsumo?"+ $.param({"codInsumo": codInsumo}),
        success: function(result, textStatus, xhr) { 
            console.log(result)
            return result
        },
        complete: function(xhr, textStatus){
            $('#agregarInsumo').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}

async function bajaInsumo(datos){
    await $.ajax({
        type: "POST",
        url: "/insumos/baja_insumos",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
        },
        complete: function(xhr, textStatus){
            $('#baja-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}

async function agregarProducto(datos){
    return await $.ajax({
        type: "POST",
        url: "/productos/agregar_producto",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result)
            return result
        },
        complete: function(xhr, textStatus){
            $('#agregar').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}

async function editarProducto(datos)
{
    $('#guardaCambios').prop('disabled', true)
    await $.ajax({
        type: "POST",
        url: "/productos/editar_producto",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result)
            return result
        },
        complete: function(xhr, textStatus){
            $('#guardaCambios').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}

async function eliminarProductoAjax(codProducto){
    $('#eliminarProducto-btn').prop('disabled', true)
    $.ajax({
        type: "POST",
        url: "/productos/eliminar_producto?"+ $.param({"codProducto": codProducto}),
        success: function(result, textStatus, xhr) { 
        },
        complete: function(xhr, textStatus){
            $('#eliminarProducto-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}

async function agregarEquipo(datos){
    $.ajax({
        type: "POST",
        url: "/equipos/agregar_equipo",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            location.reload()
        },
        complete: function(xhr, textStatus){
            $('#agregarEquipo-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            if(e.status == 422)
                alert(e.responseJSON.msg)
            else
                alert(e.statusText)
        }
    });
}

async function datosEquipo(id){
    return await $.ajax({
        type: "GET",
        url: "/equipos/datos/?"+ $.param({"id": id}),
        success: function(result, textStatus, xhr) { 
            return result
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}

async function agregarMantenimiento(datos){
    $.ajax({
        type: "POST",
        url: "/equipos/agregar_mantenimiento",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            location.reload()
        },
        complete: function(xhr, textStatus){
            $('#agregarEquipo-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            if(e.status == 422)
                alert(e.responseJSON.msg)
            else
                alert(e.statusText)
        }
    });
}

async function eliminarEquipoAjax(id){
    $.ajax({
        type: "POST",
        url: "/equipos/eliminar_equipo?"+ $.param({"id": id}),
        success: function(result, textStatus, xhr) { 
            location.reload()
        },
        complete: function(xhr, textStatus){
            $('#eliminarEquipo-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}