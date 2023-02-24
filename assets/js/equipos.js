IDEQUIPO = null
$(document).ready(function(){
    var tipo = $('#tipoEquipo :selected')
    if(tipo.val() == 'other'){
        $('.otherTipo').prop('hidden', false)
    }
    else
        $('.otherTipo').prop('hidden', true)
    
    var marcar = $('#marca :selected')
    if(marcar.val() == 'other'){
        $('.otherMarca').prop('hidden', false)
        
    }
    else
        $('.otherMarca').prop('hidden', true)  
    

    var tipoTrabajo = $('#tipoTrabajo :selected')
    if(tipoTrabajo.val() == 'other'){
        $('.otherTipoTrab').prop('hidden', false)
    }
    else
        $('.otherTipoTrab').prop('hidden', true)
    $('#fechaMantenimiento, #fecha').attr('max', date(1));
})

async function infoEquipo(id){
    IDEQUIPO = id
    var equipo = await datosEquipo(id)
    console.log(equipo)
    $('#infoEquipo-modal').modal('show')
    $('#numSerie').val(equipo.numSerie)
    $('#marca').val(equipo.marcaEquipo.descripcion)
    $('#tipo').val(equipo.tipoEquipo.descripcion)
    $('#modelo').val(equipo.modelo)
    $('#fechaAdqui').val(equipo.fechaAdquisicion)
}

function eliminarEquipo(id){
    IDEQUIPO = id
    $('#eliminarEquipo-modal').modal('show')
}

$('#eliminarEquipo-btn').click(async function(){
    $('#eliminarEquipo-btn').prop('disabled', true)
    var e = await eliminarEquipoAjax(IDEQUIPO)
})

$('#mantenimientos-btn').click(function(){
    location.href = '/equipos/mantenimientos?id='+IDEQUIPO
})

$('#marca').change(function(){
    var marca = $('#marca :selected')
    if(marca.val() == 'other'){
        $('.otherMarca').prop('hidden', false)
    }
    else{
        $('.otherMarca').prop('hidden', true)
    }
})
$('#tipoEquipo').change(function(){
    var tipo = $('#tipoEquipo :selected')
    if(tipo.val() == 'other')
        $('.otherTipo').prop('hidden', false)
    else
        $('.otherTipo').prop('hidden', true)
})


$('#agregarEquipo-btn').click(async function(){
    var numSerie = $('#numeroSerie')
    var marca = $('#marca')
    var modelo = $('#modelo')
    var fecha = $('#fecha')
    var tipoEquipo = $('#tipoEquipo')
    var otherMarca = $('#otherMarca')
    var otherTipo = $('#otherTipo')
    if(numSerie.val() == ''){
        numSerie.focus()
        return 0
    }
    if(marca.val() == ''){
        marca.focus()
        return 0
    }
    if(modelo.val() == ''){
        modelo.focus()
        return 0
    }
    if(marca.val() == 'other' && otherMarca.val() == ''){
        otherMarca.focus()
        return 0
    }
    if(fecha.val()== ''){
        fecha.focus()
        return 0
    }
    if(tipoEquipo.val() == '' ){
        tipoEquipo.focus()
        return 0
    }
    if(tipoEquipo.val()== 'other' && otherTipo.val()=='' ){
        otherTipo.focus()
        return 0
    }
    var data = {
        numSerie: numSerie.val(),
        modelo: modelo.val(),
        fechaAdquisicion: fecha.val(),
        tipoEquipo: {
            tipo_id: tipoEquipo.val()
        },
        marcaEquipo: {
            marca_id: marca.val()
        }
    }
    if(tipoEquipo.val() == 'other'){
        data.tipoEquipo.descripcion = otherTipo.val()
    }
    if(marca.val() == 'other')
        data.marcaEquipo.descripcion = otherMarca.val()

    $('#agregarEquipo-btn').prop('disabled', true)
    await agregarEquipo(data)

})

$('#agregarMantenimiento-btn').click(async function(){
    var fecha = $('#fechaMantenimiento')
    var tipoTrabajo = $('#tipoTrabajo :selected')
    var descripcion = $('#descripcion')
    if(fecha.val() == ''){
        fecha.focus()
        return 0
    }
    if(tipoTrabajo.val() == ''){
        tipoTrabajo.focus()
        return 0
    }
    var otherTipo = $('#otherTipo')
    if(tipoTrabajo.val() == 'other' && otherTipo.val() == ''){
        otherTipo.focus()
        return 0
    }
    var datos ={
        idEquipo : IDEQUIPO,
        fecha: fecha.val(),
        descripcion : descripcion.val(),
        tipoMantenimiento : {
            tipo_id : tipoTrabajo.val()
        }
    }
    if(tipoTrabajo.val() == 'other')
    datos.tipoMantenimiento.descripcion = otherTipo.val()
    await agregarMantenimiento(datos)
})

$('#tipoTrabajo').change(function(){
    var tipoTrabajo = $('#tipoTrabajo :selected')
    if(tipoTrabajo.val() == 'other')
        $('.otherTipoTrab').prop('hidden', false)
    else
        $('.otherTipoTrab').prop('hidden', true)
})


$('#cancelar').click(function(){
    location.reload()
})
