$('#ajustes-form').submit(function (e) {
    $('#guardar-btn').html('Guardar');
    e.preventDefault();
    var datos = {
        delivery: {
            costoDelivery: $('#costoDelivery').val(),
        },
        senas:{
            monto: $('#montoSena').val()
        }
    }
    $.ajax({
        type: "PUT",
        url: "/ajustes/actualizar",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            $('#guardar-btn').html('<i class="ri-check-double-line"></i>');
        },
        complete: function(xhr, textStatus){
            $('#guardarCambios-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
});