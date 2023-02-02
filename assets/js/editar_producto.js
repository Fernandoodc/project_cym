CONT = 0
CONTMAYO = 0
DATOS = {
    insumos_producto: [],
    preciosMayoristas: [],
    metodoCalculo: {
        codMetodo: 0,
        descripcion: ''
    }
}

const funcInsumo = async () => {
    var insumo = $("#insumo :selected")
    $('#agregarInsumo').prop('disabled', true)
    TIPOINSUMO = await tipoInsumo(insumo.val())
    TIPOINSUMO = TIPOINSUMO.tipoInsumo_id
    if(TIPOINSUMO != 1){
        $('#cantidad-div').hide()  
    }else{
        $('#cantidad-div').show()
    }
}

$('#insumo').change(funcInsumo)
$('#agregarInsumo').click(function(){
    var cantidad = $('#cantidadInsumo')
    var insumo = $("#insumo :selected")
    var datosInsumo = {
        codInsumo: insumo.val()
    }
    if(TIPOINSUMO == 1){
        if(cantidad.val() < 0){
            cantidad.focus()
            return 0;
        }
        datosInsumo.cantidad = parseInt(cantidad.val())
    }
    DATOS.insumos_producto.push(datosInsumo)
    var newRow = $("<tr>");
    newRow.attr('class', datosInsumo.codInsumo + '-' + datosInsumo.cantidad);
    var cols = "";
    cols += '<td>' + insumo.text() +'</td>';
    newRow.append(cols);
    cols = '<td>'+ cantidad.val() +'</td>'
    newRow.append(cols);
    cols = '<td><button type="button" class="btn btn-danger" onclick="eliminarInsumo('+"'"+ datosInsumo.codInsumo+"'" + "," + datosInsumo.cantidad +')"><i class="ri-delete-bin-2-line"></i></button></td>'
    newRow.append(cols);
    $("#insumos-tbody").append(newRow);
    CONT++
    cantidad.val('')
})

$('#mayoristasAgregar').click(function(){
    var desde = $('#mayoristasDesde')
    var precio = $('#mayoristasPrecio')
    if(desde.val() <= 1 ){
        desde.focus()
        return 0;
    }
    if(precio < 0){
        precio.focus()
        return 0;
    }
    var datosMayoristas = {
        cantidad: parseInt(desde.val()),
        precio: parseInt(precio.val())
    }
    DATOS.preciosMayoristas.push(datosMayoristas)
    var newRow = $("<tr>");
    newRow.attr('class', datosMayoristas.cantidad +'-'+datosMayoristas.precio);
    var cols = "";
    cols += '<td>' + desde.val() +'</td>';
    newRow.append(cols);
    cols = '<td>'+ precio.val() +'</td>'
    newRow.append(cols);
    cols = '<td><button type="button" class="btn btn-danger" onclick="eliminarMayorista('+"'" + datosMayoristas.cantidad+"'" +", '"+datosMayoristas.precio+"'" +')"><i class="ri-delete-bin-2-line"></i></button></td>'
    newRow.append(cols);
    $("#mayoristas-tbody").append(newRow);
    CONTMAYO++
})

$('#agregar').click(async function(){
    var descripcion = $('#descripcion')
    var precioBase = $('#precioBase')
    var metodoCalculo = $("#metodoCalculo :selected")
    if(descripcion.val() == ''){
        descripcion.focus()
        return 0
    }
    if(precioBase.val() < 0){
        precioBase.focus()
    }
    DATOS.descripcion = descripcion.val()
    DATOS.precioBase = precioBase.val()
    DATOS.metodoCalculo.codMetodo = parseInt(metodoCalculo.val())
    DATOS.metodoCalculo.descripcion = metodoCalculo.text()
    $('#agregar').prop('disabled', true)
    codProducto = await agregarProducto(DATOS)
    var HtmlCod = ' <p class="text border-bottom">Código de Insumo: <strong>'+ codProducto +'</strong></p>'
    $('#codProducto-div').append(HtmlCod)
    $('#agregar').hide()
    $('#cancelar').removeClass('btn-secondary')
    $('#cancelar').addClass('btn-primary')
    $('#cancelar').html('Agregar Otro')
    $('#cancelar').focus()
})

$('#cancelar').click(function(){
    location.reload()
})

function eliminarInsumo(cod, cant){
    aux = DATOS.insumos_producto.length
    for(i = 0; i < DATOS.insumos_producto.length ; i++){
        if(DATOS.insumos_producto[i].cantidad == cant && DATOS.insumos_producto[i].codInsumo== cod){
            DATOS.insumos_producto.splice(i,1)
            i = -1
        }
    }
    $('.'+cod+'-'+cant).remove() .splice(0,1)
}
function eliminarMayorista(cant, precio){
    for(i = 0 ; i< DATOS.preciosMayoristas.length ; i++){
        if(DATOS.preciosMayoristas[i].cantidad == cant && DATOS.preciosMayoristas[i].precio == precio){
            DATOS.preciosMayoristas.splice(i, 1)
            i = -1
        }
    }
    $('.'+cant+'-'+precio).remove()
}


funcInsumo()
