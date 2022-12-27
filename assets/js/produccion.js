
async function info(codProd){
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

    $("#checkAprovado").prop("checked", data.aprovado);

    if(data.archivos != undefined){
        for(let i = 0; i<data.archivos.length; i++){
            var newRow = $("<tr>");
            var cols = "";
            cols += '<td><a href="/files?codPedido='+ data.codPedido + '&codDet='+ data.codDetalle +'&filename='+ data.archivos[i].nombre +'" > '  +data.archivos[i].nombre+"</a></td>";
            newRow.append(cols);
            cols = '<td><button type="button" class="btn btn-primary">Descargar</button></td>'
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
    if(data.etapa.codEtapa == 0){
        $("#btnProduccion").html('Iniciar Producción')
    }else{
        if((data.etapa.codEtapa == 1)){
            $("#btnProduccion").html('Continuar Producción')
        }
    }
    //$("#infoDisenios").html('');
    $("#infoCant").val((data.cantidad-data.cantidadRestante) + " de "+ data.cantidad)
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
            cols = '<td><button type="button" class="btn btn-primary">Descargar</button> <button type="button" value='+ files[i].descripcion +' onclick="eliminarDisenio('+ "'" + files[i].descripcion + "'" +')" class="btn btn-danger">Eliminar</button></td>'
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
})

async function eliminarDisenio(filename){
    console.log("click")
    await deleteDesing(data.codPedido, data.codDetalle, data.codProduccion, filename)
    await info(data.codProduccion)
}