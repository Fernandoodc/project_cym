CODPEDIDO = null
FACTURA = null
NUMRECIBO = null
SALDO = null
BANDPRINT = false
id_cliente = ''
async function registrarPago(datos) {
    var response
    await $.ajax({
        type: "POST",
        url: "/pagos/registrar_pago",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function (result) {
            response = result

        },
        error: function (e) {
            console.log(e)
            alert(e.statusText)

        }
    });
    return response;
}

async function generarFactura(datos) {
    var response
    await $.ajax({
        type: "POST",
        url: "/pagos/generar_factura",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function (result) {
            console.log(result)
            response = result

        },
        error: function (e) {
            console.log(e)
            alert(e.statusText)

        }
    });
    return response;
}
async function obtenerCuentas(documento){
    var respose = null
    await $.ajax({
        type: "GET",
        url: "/clientes/deudas?"+ $.param({"documento": documento}),
        success: function(result, textStatus, xhr) { 
            respose = result
            $('#alertDocumento').prop('hidden', true)
        },
        complete: function(xhr, textStatus){
            $('#documento').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            if(e.status == 404){
                $('#alertDocumento').prop('hidden', false)
            }else{
                alert(e.statusText)
            }
        }
    });
    return respose
}

async function abonar(codPedido){
    $('#entregarPedido-btn').html('Entregar Pedido/s')
    $('#entregarPedido-btn').prop('disabled', false)
    $('.btn-abonar').prop('disabled', true)
    $('#btn-factura-div').hide()
    $('#imprimirRecibo').hide()
    await $.ajax({
        type: "GET",
        url: "/pagos/info_cuenta?"+ $.param({"codPedido": codPedido}),
        success: function(result, textStatus, xhr) { 
            $('#codPedido').text(result.codPedido)
            $('#total').text(result.total)
            $('#saldo').html('<b>Saldo:</b> ' + result.saldo)
            CODPEDIDO = result.codPedido
            $('#newCliente').prop('hidden', true)
            SALDO = result.saldo
            $('#monto').attr({
                "max" : result.saldo,     
                "min" : 0       
            });
            if(result.saldo > 0){
                $('#monto').show()
                $('#registrarPago').show()
            }else{
                $('#registrarPago').hide()
                $('#monto').hide()
            }
            if(result.estadoProduccion.produccionTerminada == true && result.entregados == false){
                $('#entregarPedido-btn').show()
            }else
                $('#entregarPedido-btn').hide()

            $('#abonar-modal').modal('show')
            
        },
        complete: function(xhr, textStatus){
            $('.btn-abonar').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
    FACTURA = null

}

const imprimirFactura = async (cliente_id, codPedido) => {
    if(FACTURA == null){
        datos = {
            codPedido: [codPedido],
            cliente_id: cliente_id
        }
        FACTURA = await generarFactura(datos)
    }
    window.open(
        '/pagos/imprimir_factura/' + FACTURA.numeroFactura,
        '_blank'
    );
}

$('#buscarCuentas').click(async function(){
    $("#bodyLista").html('')
    $('#nombre').val('')
    var documento = $('#documento')
    if(documento.val() == ''){
        documento.focus()
    }
    documento.prop('disabled', true)
    var cuentas =  await obtenerCuentas(documento.val())
    id_cliente = cuentas.datosCliente._id['$oid']
    $('#nombre').val(cuentas.datosCliente.nombre + ' ' +cuentas.datosCliente.apellido)
    cuentas.cuentas.forEach(cuenta => {
        //console.log(cuenta)
        var newRow = $('<tr id="'+ cuenta.codPedido +'">');
        var cols = "";
        cols += "<td>" +cuenta.codPedido + "</td>" ;
        newRow.append(cols);
        var newUl = $('<ul>')
        var li = ''
        cuenta.detallesPedido.forEach(pedido => {
            li = "<li>" + pedido.producto.descripcion + "</li>"
            newUl.append(li)
        });
        cols = $('<td>')
        cols.append(newUl)
        newRow.append(cols)
        cols = "<td>" + cuenta.pedido.fecha + "</td>"
        newRow.append(cols)
        cols = "<td>" + cuenta.total +"</td>"
        newRow.append(cols)
        cols = "<td class='text-danger saldo'>" + cuenta.saldo +"</td>"
        newRow.append(cols)
        cols = "<td>"+ '<button type="button" class="btn btn-success btn-abonar" onclick="abonar('+ "'" +cuenta.codPedido + "'" +')">Abonar</button>' +"</td>"
        newRow.append(cols)
        $("#bodyLista").append(newRow);
    });
})


$('#registrarPago').click(async function () {
    var monto = $('#monto')
    if (monto.val() <= 0 || monto.val() > SALDO) {
        monto.focus()
        return 0;
    }
    var datos = {
        monto: monto.val(),
        codPedido: CODPEDIDO,
        cliente_id: id_cliente
    }
    var pago = await registrarPago(datos)
    if(pago.saldo <= (pago.total/2)){
        $('#help').hide();
    }
    BANDPRINT = true
    SALDO = pago.saldo
    NUMRECIBO = pago.numeroRecibo
    $('#saldo').html('<b>Saldo:</b> ' + pago.saldo)
    //pago parcial
    $('#'+CODPEDIDO + ' .saldo').text(pago.saldo)
    if (pago.saldo > 0) {
        $('#imprimirRecibo').show()
    } else { //pago total
        if (pago.saldo <= 0) {
            $('#monto').hide()
            $('#imprimirFactura').show()
            $('#imprimirRecibo').show()
            $('.otherCliete').show()
            $('#registrarPago').hide()
            $('#btn-factura-div').show()
        }
    }
    $('#monto').attr({
        "max" : pago.saldo,     
        "min" : 0       
    });
    $('#monto').val('')
    $('.btn-close').remove()
})

$('#imprimirRecibo').click(function () {
    window.open(
        "/pagos/imprimir_recibo/" + NUMRECIBO,
        '_blank'
    );
})

$('#imprimirFactura').click(function(){
    $('.otherCliete').hide()
    imprimirFactura(id_cliente, CODPEDIDO)
})

$('#otherCliete').change(function(){
    var check = $('#otherCliete')
    if(check.is(':checked') == true){
        $('#newCliente').prop('hidden', false)
        $('#imprimirFactura').prop('disabled', true)
    }
    else{
        $('#newCliente').prop('hidden', true)
        $('#imprimirFactura').prop('disabled', false)
    }
})


$('#newDocumento, .newDocumento').change(async function(e){
    e.preventDefault();
    var documento = $('#newDocumento').val()
    setTimeout(async () => {
        await $.ajax({
            type: "GET",
            url: "/clientes/get_client/?"+ $.param({"doc": documento}),
            success: function(result, textStatus, xhr) { 
                $('.infoCliente').prop('disabled', true)
                $('#newNombre').val(result.nombre)
                $('#newApellido').val(result.apellido)
                $("#newNacionalidad").val(result.nacionalidades_id).change();
                $('#newDireccion').val(result.direccion)
                $('#newCelular').val(result.celular)
                $('#newEmail').val(result.email)
                $('#printFactura').click(function(){
                    $('#newDocumento').prop('disabled', true)
                    imprimirFactura(result._id['$oid'], CODPEDIDO)
                })
                
            },
            complete: function(xhr, textStatus){
                $('#documento').prop('disabled', false)
            },
            error: function(e){
                $('.infoCliente').prop('disabled', false)
                $('#newNombre').val('')
                $('#newApellido').val('')
                $("#newNacionalidad").val('PY').change();
                $('#newDireccion').val('')
                $('#newCelular').val('')
                $('#newEmail').val('')
            }
        });
    }, 500);
})
