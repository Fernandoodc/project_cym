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