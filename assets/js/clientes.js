DOCUMENTO = null
CLIENTE = null
async function datosCliente(cliete_id){
    DOCUMENTO = CLIENTE = null
    $('#editar-cliente').show()
    $('#guardar').hide()
    $('.infoCliente').prop('disabled',true)
    CLIENTE = await infoCliente(cliete_id)
    DOCUMENTO = CLIENTE.documento
    $('#infoCliente-modal').modal('show')
    $('#documento').val(CLIENTE.documento)
    $('#nombre').val(CLIENTE.nombre)
    $('#apellido').val(CLIENTE.apellido)
    $('#nacionalidad').val(CLIENTE.nacionalidades_id).change()
    $('#direccion').val(CLIENTE.direccion)
    $('#celular').val(CLIENTE.celular)
    $('#email').val(CLIENTE.email)
    $('#saldo').val(CLIENTE.saldo)
}

$('#abonar-btn').click(function () {
    if(DOCUMENTO == null)
        return 0
    window.open(
        "/pagos/cobranza?documento=" + DOCUMENTO,
        '_blank'
    );
})
$('#historialPagos-btn').click(function () {
    if(DOCUMENTO == null)
        return 0
    window.open(
        "/clientes/historial_pagos/" + CLIENTE._id['$oid'],
        '_blank'
    );
})
$('#historialPedidos-btn').click(function () {
    if(DOCUMENTO == null)
        return 0
    window.open(
        "/clientes/historial_pedidos/" + CLIENTE._id['$oid'],
        '_blank'
    );
})

$('#editar-cliente').click(function(){
    $('.infoCliente').prop('disabled',false)
    $('#editar-cliente').hide()
    $('#guardar').show()
})
$('#guardar').click(async function(){
    var nombre = $('#nombre')
    var apellido = $('#apellido')
    var nacionalidad = $('#nacionalidad :selected')
    var direccion = $('#direccion')
    var celular = $('#celular')
    var email = $('#email')
    if(nombre.val == ''){
        nombre.focus()
        return 0
    }
    if(apellido.val() == ''){
        apellido.focus()
        return 0
    }
    if(nacionalidad.val == ''){
        nacionalidad.focus()
        return 0
    }
    var id_cliente = CLIENTE._id['$oid']
    var cliente = CLIENTE
    cliente.nombre = nombre.val()
    cliente.apellido = apellido.val()
    cliente.nacionalidad = nacionalidad.val()
    cliente.direccion = direccion.val()
    cliente.celular = celular.val()
    cliente.email = email.val()

    delete cliente.saldo
    delete cliente._id

    $('#guardar').prop('disabled', true)
    var result = await editarCliente(cliente, id_cliente)
    $('#editar-cliente').show()
    $('#guardar').hide()
    $('.infoCliente').prop('disabled',true)
    $('#'+id_cliente + ' .nombre').text(cliente.nombre)
    $('#'+id_cliente + ' .apellido').text(cliente.apellido)
    
})