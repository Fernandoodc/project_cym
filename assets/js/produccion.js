
async function info(codProd){
    $("#infoCod").val('');
    $("#infoTipo").val('');
    $("#infoDescripcion").val('');
    $("#infoArchivos").html('');
    $("#infoDisenios").html('');
    $("#infoCant").val('0 de 0')
    data = await infoProduccion(codProd);
    data = data[0]
    console.log(data);
    $("#infoCod").val(codProd);
    $("#infoTipo").val(data.producto);
    $("#infoDescripcion").val(data.descripcion);
    if(data.archivos != undefined){
        console.log(true)
        /*table = document.getElementById("infoArchivos");
        var row = table.insertRow();
        var cell = row.insertCell();
        cell.innerHTML = "TEXT";*/
        for(let i = 0; i<data.archivos.length; i++){
            console.log(i)
           /*var tr = document.createElement("tr")
           var tdArc = document.createElement("td")
           var tdBtn = document.createElement("td")
           tdArc.innerHTML = "<p>"+data.archivos[i].nombre+"</p>"
           tdBtn.innerHTML = '<button type="button" class="btn btn-primary">Descargar</button>'
           tr.appendChild(tdArc);
           tr.appendChild(tdBtn);
           console.log(tr)
           document.getElementById("infoArchivos").appendChild(tr)*/
            var newRow = $("<tr>");
            var cols = "";
            cols += '<td><a href="/files?codPedido='+ data.codPedido + '&codDet='+ data.codProduccion +'&filename='+ data.archivos[i].nombre +'" > '  +data.archivos[i].nombre+"</a></td>";
            console.log(cols)
            newRow.append(cols);
            cols = '<td><button type="button" class="btn btn-primary">Descargar</button></td>'
            newRow.append(cols);
            $("#infoArchivos").append(newRow);
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