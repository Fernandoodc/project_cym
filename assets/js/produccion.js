$('#guardarTerminados').click(async function(){
    if($('#terminado').val()<=0){
        $('#terminado').focus();
        return 0;
    }
    if(parseInt($('#terminado').val()) >  parseInt($('#terminado').attr('max'))){
        $('#terminado').focus();
        return 0;
    }
    data = {
        codProduccion: codProduccion,
        cantidad: $('#terminado').val()
    }
    console.log(data)
    $('#guardarTerminados').prop('disabled', true)
    var cant = await enviarTerminados(data)
    console.log(cant)
    $('#guardarTerminados').prop('disabled', false)
    var producido = cant.cantidad - cant.cantidadRestante
    $('#progreso').css("width", producido*100 / cant.cantidad+"%")
    $('#progreso-p').html(producido + ' de ' + cant.cantidad)
    $('#terminado').val('')
    $("#terminado").attr({
        "max" : cant.cantidadRestante,
    })
    if(cant.cantidadRestante <= 0){
        $('#terminado-modal').modal('show')
        $('#btn-terminar').focus()
        $('#producido').html(producido)
        $('#total').html(cant.cantidad)
    }else{
        if(cant.cantidadRestante < cant.cantidad){
            $('#pausar-openModal').hide()
            var button = '<button type="button" class="btn btn-secondary" id="pausar-openModal" data-bs-toggle="modal" data-bs-target="#pausar-modal">Pausar Produccion</button>'
            $('#botonesEstado').append(button)
            $('#cancelarProduccion').hide()
        }
    }

})

$('#cancelarProduccion').click(async function(){
    $('#cancelarProduccion').prop('disabled', true)
    await cancelarProduccion(codProduccion)
    $('#cancelarProduccion').prop('disabled', false)
    $('#cancelarProduccion').hide()
    window.location.href = "/trabajos/orden_trabajo"

})

$('#pausarProduccion').click(async function(){
    $('#pausarProduccion').prop('disabled', true)
    await pausarProduccion(codProduccion)
    $('#pausarProduccion').prop('disabled', false)
    window.location.href = "/trabajos/orden_trabajo"

})

$('#btn-terminar').click(function(){
    window.location.href = "/trabajos/orden_trabajo"
})

$('#solicitarInsumo').click(async function(){
    var cantidad = $('#cantidadPerdidad')
    var comentarios = $('#comentarios')
    var insumo = $('#insumo :selected')
    
    if(cantidad.val()<=0){
        cantidad.focus()
        return 0;
    }
    if(comentarios.val() == ''){
        comentarios.focus();
        return 0;
    }
    var datos = {
        'codInsumo': insumo.val(),
        'codProduccion': codProduccion,
        'cantidad': cantidad.val(),
        'comentarios': comentarios.val()
    }
    console.log(datos)
    $(this).prop('disabled', true)
    var info = await solicitarInsumos(datos)
    console.log(info)
    if(info == false){
        $('#alertPedida').addClass('alert-danger')
        $('#alertPedida').html('No se cuenta con el stock suficiente del insumo solicitado')
    }
    else{
        $('#alertPedida').html('')
        $('#alertPedida').removeClass('alert-danger')
    }
    $(this).prop('disabled', false)
    cantidad.val(0)
    comentarios.val('')
    var newRow = $("<tr>");
    var cols = "";
    cols += '<td>'+insumo.text()+'</td>'
    newRow.append(cols)
    cols =  '<td>'+datos.cantidad+'</td>'
    newRow.append(cols)
    $('#listPerdidos').append(newRow);


$('#solicitarInsumo-btn').click(function(){
    $('#alertPedida').html('')
    $('#alertPedida').removeClass('alert-danger')
})


})