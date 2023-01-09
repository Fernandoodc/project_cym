function actFecha(){
    var fecha = facturas[$('#facturas').prop('selectedIndex')].fecha
    $('#fecha').val(fecha)
    
}
$('#aggProveedor').click(async function(){
    if($('#rucProveedor').val() == ''){
        $('#rucProveedor').focus()
        return 0
    }
    if($('#nombreProveedor').val() == ''){
        $('#nombreProveedor').focus()
        return 0
    }
    var data = {
        'ruc': $('#rucProveedor').val(),
        'nombre': $('#nombreProveedor').val(),
        'direccion': $('#direccionProveedor').val(),
        'celular': $('#celularProveedor').val(),
        'email': $('#emailProveedor').val()
    }
    var proveedor = await agregarProveedor(data)
    if(proveedor == 409){
        $('#alertNuevoProveedor').addClass('alert-danger')
        $('#alertNuevoProveedor').html('Proveedor ya Existente')
        return 0
    }
    $('#proveedores').append($("<option>", {
        value: data.ruc,
        text: data.nombre
      }));
    $("#proveedores option[value='"+ data._id + "']").attr("selected", true);
    $('#rucProveedor').val('')
    $('#nombreProveedor').val('')
    $('#direccionProveedor').val('')
    $('#celularProveedor').val('')
    $('#emailProveedor').val('')
    $('#newProveedor-modal').modal('hide');

})

const actListaFacturas = async () => {
    $('#facturas').html('')
    var proveedor =  $("#proveedores :selected").val()
    facturas = await listaFacturas(proveedor)
    console.log(facturas)
    for(var i = 0; i < facturas.length ; i++){
        $('#facturas').append($("<option>", {
            value: facturas[i]._id.$oid,
            text: facturas[i].numeroFactura
        }));
    }
    actFecha()
}
$('#newFactura').click(function(){
    $('#infoProveedor').val($("#proveedores :selected").text())

})
$('#aggFactura').click(async () => {
    if($('#newNumeroFactura').val() == ''){
        $('#newNumeroFactura').focus()
        return 0
    }
    if($('#newFechaFactura').val() == ''){
        $('#newFechaFactura').focus()
        return 0
    }
    var data = {
        'fecha': $('#newFechaFactura').val(),
        'numeroFactura': $('#newNumeroFactura').val(),
        'Proveedores_id': $("#proveedores :selected").val()
    }
    console.log(data)
    await agregarFactura(data)
    $('#facturas').append($("<option>", {
        value: data.Proveedores_id,
        text: data.numeroFactura
    }));
    $('#alertNuevaFactura').html('')
    $('#newNumeroFactura').val('')
    $('#newFechaFactura').val('')
    $('#newFactura-modal').modal('hide')

})

$('#btn-newInsumo').click(function(){
    $('#btn-ok').hide()
    $('#div-codInsumo').hide()
})

$('#aggInsumo').click(async function(){
    var desc =  $('#descripcionInsumo')
    var stockMin = $('#stockMin')
    if(desc.val() == ''){
        desc.focus()
        return 0;
    }
    if(stockMin.val() == '' || stockMin.val < 0){
        stockMin.focus()
        return 0;
    }
    var data = {
        "descripcion": desc.val(),
        "stockMin": stockMin.val(),
        "tipoInsumo_id": $("#tipoInsumo").val()
    }
    console.log(data)
    var codInsumo = await agregarInsumo(data);
    $('#cancelarNewInsumo').hide()
    $('#aggInsumo').hide()
    $('#div-codInsumo').show()
    $('#btn-ok').show()
    $('#btn-ok').focus()
    $('#codInsumo').val(codInsumo)
    $('#insumo').append($("<option>", {
        value: codInsumo,
        text: codInsumo + "-" + data.descripcion
    }));
})

$("#btn-ok").click(function(){
    $('#stockMin').val('')
    $('#descripcionInsumo').val('')
    $('#cancelarNewInsumo').show()
    $('#aggInsumo').show()
    $('#newInsumo-modal').modal('hide')
})

$("#agregar").click(async function(){
    var precioUnitario = $("#precioUnitario")
    var cantidad = $('#cantidad')
    var factura = $("#facturas :selected")
    var insumo = $("#insumo :selected")
    if(factura.prop('selectedIndex') == -1 ){
        $("#factuas").focus()
        return 0
    }
    if(insumo.prop('selectedIndex') == -1) {
        $("#insumo").focus()
        return 0
    }
    if(precioUnitario.val() == '' || precioUnitario <= 0){
        precioUnitario.focus()
        return 0
    }
    if(cantidad.val()<=0 || cantidad.val()==''){
        cantidad.focus()
        return 0
    }

    var datos = {
        codInsumo : insumo.val(),
        precioUnitario : precioUnitario.val(),
        cantidad : cantidad.val(),
        FacturasProveedores_id : factura.val()
    }

    //$('#agregar').prop('disabled', true)
    var idCompra = await registrarCompra(datos)
    //$('#agregar').prop('disabled', false)
    var newRow = $("<tr>");
    newRow.attr('id', idCompra);
    var cols = "";

    cols += "<td>"+ factura.text() +"</td>";
    newRow.append(cols);
    
    
    cols = '<td>'+ insumo.text() +'</td>'
    newRow.append(cols);

    cols = '<td>'+ datos.precioUnitario +'</td>'
    newRow.append(cols);

    cols = '<td>'+ datos.cantidad +'</td>'
    newRow.append(cols);
     
    var total = datos.precioUnitario * datos.cantidad
    cols = '<td id="total-'+ idCompra +'" >'+ total +'</td>'
    newRow.append(cols);

    cols = '<td><button type="button" onclick="eliminarCompra('+ "'" + idCompra + "'" +')" class="btn btn-danger">Eliminar</button></td>'
    newRow.append(cols);
    $("#listaCompras").append(newRow);
    $('#total').html(parseInt($('#total').html()) + total)
    precioUnitario.val('')
    cantidad.val('')

})

$('#limpiar').click(function(){
    location.reload()
})

async function eliminarCompra(id){
    await eliminarCompraAjax(id)
    var precio = parseInt($('#total-'+id).html())
    $('#total').html(parseInt($('#total').html()) - precio)
    $('#'+id).hide()

}

$("#proveedores").change(actListaFacturas)
$('#facturas').change(function(){
    actFecha()
})
actListaFacturas();