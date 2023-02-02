
async function info(codProd){
    $('#alertProduccion').html('')
    $('#alertProduccion').removeClass( "alert-danger" )
    $("#infoCod").val('');
    $("#infoTipo").val('');
    $("#infoDescripcion").val('');
    $("#infoArchivos").html('');
    $("#infoDisenios").html('');
    $("#infoCant").val('0 de 0')
    data = await infoProduccion(codProd);
    console.log(data)
    data = data[0]
    console.log(data)
    $("#infoCod").val(data.codProduccion);
    $("#infoTipo").val(data.producto);
    $("#infoDescripcion").val(data.descripcion);

    if(data.detalleProducto.metodoCalculo.codMetodo == 1){
        $("#dimensiones").hide()
    }
    else{
        $("#dimensiones").show()
        $("#ancho").val(data.detalleProducto.medidas.ancho)
        $("#alto").val(data.detalleProducto.medidas.alto)
    }
    if(data.aprovado != undefined)
        $("#checkAprovado").prop("checked", data.aprovado);
    else
    $("#checkAprovado").prop("checked", false);

    if(data.archivos != undefined){
        for(let i = 0; i<data.archivos.length; i++){
            var newRow = $("<tr>");
            var cols = "";
            //cols += '<td><a href="/files?codPedido='+ data.codPedido + '&codDet='+ data.codDetalle +'&filename='+ data.archivos[i].nombre +'" > '  +data.archivos[i].nombre+"</a></td>";
            cols += '<td><a href="/files?ruta='+ data.archivos[i].ruta +'" > '  + data.archivos[i].nombre+ "</a></td>";
            newRow.append(cols);
            cols = '<td><td><a class="btn btn-primary" href="/files/download?ruta='+ data.archivos[i].ruta +'&filename='+ data.archivos[i].nombre +'" role="button">Descargar</a></td></td>'
            newRow.append(cols);
            $("#infoArchivos").append(newRow);
        }  
    }
    if(data.diseños != undefined){
        for(let i = 0; i<data.diseños.length; i++){
            console.log(i)
            var newRow = $("<tr>");
            var cols = "";
            cols += '<td><a href="/get_disenios?ruta='+ data.diseños[i].ruta +'" > '  + data.diseños[i].descripcion+"</a></td>";
            newRow.append(cols);
            cols = '<td><button type="button" class="btn btn-primary">Descargar</button> <button type="button" value='+ data.diseños[i].descripcion +' onclick="eliminarDisenio('+ "'" + data.diseños[i].descripcion + "'" +')" class="btn btn-danger">Eliminar</button></td>'
            newRow.append(cols);
            $("#infoDisenios").append(newRow);
        }
    }
    $("#btnProduccion").show()
    if(data.etapa.codEtapa == 0){
        $("#btnProduccion").html('Iniciar Producción')
        $('#aprovado-div').show()
        $('#formDiseño').show()
    }else{
        if((data.etapa.codEtapa == 1)){
            $("#btnProduccion").html('Continuar Producción')
            $('#aprovado-div').hide()
            $('#formDiseño').hide()
        }else{
            if(data.etapa.codEtapa == 2){
                $("#btnProduccion").hide()
                $('#aprovado-div').hide()
                $('#formDiseño').hide()
            }else{
                if(data.etapa.codEtapa == 3){
                    $("#btnProduccion").html('Restablecer Producción')
                    $('#aprovado-div').hide()
                    $('#formDiseño').hide()
                }
            }
        }
    }
    //$("#infoDisenios").html('');
    $("#infoCant").val((data.cantidad-data.cantidadRestante) + " de "+ data.cantidad)
    $('#detalleTrabajo').modal('show')
}

$("#aggDiseño").on("click", async function(){
    if(document.getElementById("files").value != ''){
        let form = document.getElementById("formDiseño")
        let desing = new FormData(form);
        desing.append("cod_pedido", data.codPedido);    
        desing.append("cod_detalle", data.codDetalle);
        desing.append("cod_produccion", data.codProduccion)
        console.log(desing.get("cod_pedido"))
        console.log(desing.get("cod_detalle"))
        console.log(desing.get("cod_produccion"))
        console.log(desing.get("files"))
        $("#aggDiseño").prop("disabled", true)
        files = await uploaDesign(desing);
        $("#aggDiseño").prop("disabled", false)
        for(let i = 0; i<files.length; i++){
            var newRow = $("<tr>");
            var cols = "";
            cols += '<td><a href="/get_disenios?ruta='+ files[i].ruta +'" > '  +files[i].descripcion+"</a></td>";
            newRow.append(cols);
            cols = '<td><a name="" id="" class="btn btn-primary" href="/files/download?ruta='+ files[i].ruta +'" role="button" target="_blank"><i class="ri-download-2-line"></i></a> <button type="button" value='+ files[i].descripcion +' onclick="eliminarDisenio('+ "'" + files[i].descripcion + "'" +')" class="btn btn-danger">><i class="ri-delete-bin-5-fill"></i></button></td>'
            newRow.append(cols);
            $("#infoDisenios").append(newRow);
        }
    }else
        files = []
    document.getElementById("files").value = ''
});

$("#checkAprovado").change( async function(){
    let estado = {
        "estado": $('#checkAprovado').is(":checked"),
        "codProduccion": data.codProduccion
    }
    console.log(estado)
    $("#checkAprovado").prop("disabled", true)
    await aprovacion(estado)
    $("#checkAprovado").prop("disabled", false)
    data.aprovado = estado
})

$('#btnProduccion').click(function(){
    if(!data.aprovado)
    {
        $('#alertProduccion').addClass('alert-danger')
        $('#alertProduccion').html('El diseño aún no ha sido aprovado, no se puede iniciar la producción')
        return 0;
    }
    $('#alertProduccion').html('')
    window.location.href = "/trabajos/produccion/"+data.codProduccion;
})

async function eliminarDisenio(filename){
    await deleteDesing(data.codPedido, data.codDetalle, data.codProduccion, filename)
    await info(data._id.$oid)
}