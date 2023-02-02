$('#desde').change(function(){
    $('#hasta').attr('min', $('#desde').val())
})
$('#hasta').change(function(){
    $('#desde').attr('max', $('#hasta').val())
})
$('#filtrar-noEntregados').click(function (e) { 
    var fInicio = $('#desde').val();
    var fFin = $('#hasta').val();
    location.href = '/reportes/pedidos/sin_entregar?'+$.param({'fFin': fFin, 'fInicio': fInicio})
    
});
$('#limpiar_noEntregados').click(function(){
    location.href = '/reportes/pedidos/sin_entregar'
})
$('#limpiar-resPedidos').click(function (e) { 
    e.preventDefault();
    location.href = '/reportes/pedidos/resumen'
});

$('#filtrar-resPedidos').click(function (e) { 
    e.preventDefault();
    var fInicio = $('#desde').val();
    var fFin = $('#hasta').val();
    var entrega = $('#select-entrega :selected')
    location.href = '/reportes/pedidos/resumen?'+$.param({'fFin': fFin, 'fInicio': fInicio, 'codEntrega': entrega.val()})
});

$('#limpiar-perdidosDet').click(function (e) { 
    e.preventDefault();
    location.href = '/reportes/insumos/perdidos_detalles'
});

$('#filtrar-perdidosDet').click(function (e) { 
    e.preventDefault();
    var fInicio = $('#desde').val();
    var fFin = $('#hasta').val();
    location.href = '/reportes/insumos/perdidos_detalles?'+$.param({'fFin': fFin, 'fInicio': fInicio})
});

$('#limpiar-perdidosRes').click(function (e) { 
    e.preventDefault();
    location.href = '/reportes/insumos/perdidos_resumen'
});

$('#filtrar-perdidosRes').click(function (e) { 
    e.preventDefault();
    var fInicio = $('#desde').val();
    var fFin = $('#hasta').val();
    location.href = '/reportes/insumos/perdidos_resumen?'+$.param({'fFin': fFin, 'fInicio': fInicio})
});

$('#limpiar-utilizados').click(function (e) { 
    e.preventDefault();
    location.href = '/reportes/insumos/utilizados'
});

$('#filtrar-utilizados').click(function (e) { 
    e.preventDefault();
    var fInicio = $('#desde').val();
    var fFin = $('#hasta').val();
    location.href = '/reportes/insumos/utilizados?'+$.param({'fFin': fFin, 'fInicio': fInicio})
});