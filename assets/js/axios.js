function get_client() {
    console.log('gg')
    doc = document.getElementById('documento').value
        $.ajax({
            type: "GET",
            url: "/clientes/get_client/?doc="+doc,
            
            success: function(result, textStatus, xhr) { 
               console.log(result)
                if(xhr.status == 200){
                    console.log(xhr.status)
                    //id_cliente = result._id.$oid
                    document.getElementById('nombre').value=result.nombre + " " + result.apellido
                    document.getElementById('numCelular').value = result.celular
                    document.getElementById('direccion').value = result.direccion
                }
            },
            complete: function(xhr, textStatus) {
                console.log(xhr.status)
                if(xhr.status == 404){
                    document.getElementById('nombre').value= ""
                    document.getElementById('numCelular').value = ""
                    document.getElementById('direccion').value = ""
                }
                else
                    if(xhr.status==401){
                    window.location.href = '/'
                    }
            } 
        });
    
}

async function create_pedido(data){
    let codPedido = ""
    await $.ajax({
        type: "POST",
        url: "/create_pedido",
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
        url: "/agg_detpedido",
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
        url: "/eliminar_det",
        date: codDet,
        success: function(result, textStatus, xhr) { 
            console.log(result)
            document.getElementById(codDet).remove()

        },
        complete: function(xhr, textStatus) {
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
        url: "/info_produccion/" + codProduccion,        
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