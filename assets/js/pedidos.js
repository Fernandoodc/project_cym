const select = document.getElementById('listaProductos')
//const select_var = document.getElementById('variaciones')
const cantidad = document.getElementById('cantidad')
const checkDel = document.getElementById("checkDelivery")
const agg = document.getElementById("agregar")
const aggCliente = document.getElementById("aggCliente")
const cancel = document.getElementById("cancelar")
let codMetodo = 0
precioBase = 0
precioExtra = 0
precio = 0
descuento = 0
band = false
SENAREQUIRED = false
//let variaciones = []
var pMayoristas = []
id_cliente = ""
CODPEDIDO = null
CODDETALLE = null
FECHAENTREGA = null
TOTAL = 0
SALDO = 0
BANDPRINT = false
function init(){
  $('.direccion').hide()
  var fPedido = document.getElementById("fecha_pedido")
  var fEntrega = document.getElementById("fecha_entrega")
  fPedido.value = date(1)
  fPedido.setAttribute("max", date(1))
  fEntrega.value = date()
  fEntrega.setAttribute("min", date())
  $('#divDireccion').hide()
}

function date(format=2){
  var f = new Date() 
  var year = f.getFullYear()
  var month = f.getMonth()+1
  var hour = f.getHours()
  if(f.getDate()<10){
    day = "0"+f.getDate()
  }
  else{
    day = f.getDate()
  
  }
  if(hour<10){
    hour = '0'+hour
  }
  if(f.getMinutes()<10){
    min = "0"+f.getMinutes();
  }
  else{
    min = f.getMinutes();
  }
  if(month<10){
    month = "0"+month
  }
  if (format == 1){
    return(year+"-"+month+"-"+day)
  }
  return(year+"-"+month+"-"+day +"T"+hour+":"+min)
}

async function get_client(){
  id_cliente = null
  document.getElementById('nombre').value= ""
  document.getElementById('numCelular').value = ""
  document.getElementById('direccion').value = ""
  doc = document.getElementById('documento').value
  var result = await infoCliente(doc)
  id_cliente = result._id['$oid']
  document.getElementById('nombre').value=result.nombre + " " + result.apellido
  document.getElementById('numCelular').value = result.celular
  document.getElementById('direccion').value = result.direccion
  $('#alertText').html('')
}

const prodSelected = () => {
    let indice = $('#listaProductos').prop('selectedIndex')
    if(indice === -1) return;
    console.log(indice)
    console.log(productos[indice])
    //variaciones = productos[indice].variaciones
    pMayoristas = productos[indice].preciosMayoristas

    for (i=0; i<pMayoristas.length-1; i++)
	  {
      for(z=i+1; z<pMayoristas.length; z++)
      {
        if (pMayoristas[i].cantidad>pMayoristas[z].cantidad)
        {
          aux=pMayoristas[i].cantidad;                      aux2 = pMayoristas[i].precio;
          pMayoristas[i].cantidad=pMayoristas[z].cantidad;  pMayoristas[i].precio=pMayoristas[z].precio;
          pMayoristas[z].cantidad=aux;                      pMayoristas[z].precio=aux2;
        }
      }
	  }
    console.log(pMayoristas)

    //select_var.innerHTML=""
    //console.log(variaciones.length)
    /*for(i=0; i<variaciones.length ; i++){
      option = document.createElement('option')
      option.text=variaciones[i].descripcion
      option.value=variaciones[i].codVariacion
      select_var.appendChild(option)
    }*/
    const div_calculo = document.getElementById('calculo_precio')
    codMetodo = productos[indice].metodoCalculo.codMetodo
    precioBase = productos[indice].precioBase
    if(codMetodo == 1){
      console.log('Precio Absoluto')
      div_calculo.innerHTML = ""
    }
    else if(codMetodo == 2){
      console.log('Calculo por cm2')
      div_calculo.setAttribute("class", "row mb-3")
      div_calculo.innerHTML = '<label class="col-sm-2 col-form-label">Dimensiones cm2</label><div class="col-sm-5"><label for="inputText" class="col-sm-3 col-form-label">Ancho</label> <input type="number" class="form-control" id="ancho"></div><div class="col-sm-4"><label for="inputText" class="col-sm-3 col-form-label">Alto</label> <input type="number" class="form-control" id="alto"> </div>'
    }
    else if(codMetodo == 3){
      console.log('Calculo por cm2')
      div_calculo.setAttribute("class", "row mb-3")
      div_calculo.innerHTML = '<label class="col-sm-2 col-form-label">Dimensiones m2</label><div class="col-sm-5"><label for="inputText" class="col-sm-3 col-form-label">Ancho</label> <input type="number" class="form-control" id="ancho"></div><div class="col-sm-4"><label for="inputText" class="col-sm-3 col-form-label">Alto</label> <input type="number" class="form-control" id="alto"> </div>'
    }
}
/*const varSelected = () => {
  let indice = select_var.selectedIndex;
  if(indice===-1) return;
  precioExtra = variaciones[indice].precioExtra

}*/

const actPresup = () => {
  pMayorista = 0
  mayorista = false
  //console.log("actProd")
  const presu = document.getElementById("presupuesto")
  const cant = document.getElementById("cantidad").value
  const desc = document.getElementById("descuento")
  /*if(!checkDel.checked){
    var deliv = 0
    //console.log("no check")
  }
  else var deliv = delivery
  //console.log(deliv)*/
  
  for(i=0; i<pMayoristas.length; i++){
    console.log(pMayoristas[i].cantidad)
    console.log(cant)
    if(cant>=pMayoristas[i].cantidad){

      pMayorista = pMayoristas[i].precio
      var mayorista = true
      //console.log(mayorista + " : " + pMayorista)
    }
  }

  if(codMetodo==0) return;
  else
    if(codMetodo==1){
        subTotal = (cant * (precioBase))
        total = subTotal
        if(mayorista==true){
          total = (cant * (pMayorista))
          desc.value = subTotal-total
        }
        else desc.value = 0
        
    } 
  
  if(codMetodo==2 || codMetodo==3){
    ancho = document.getElementById("ancho")
    alto = document.getElementById("alto")
    ancho.addEventListener('input', actPresup, prodSelected)
    alto.addEventListener('input', actPresup, prodSelected)
    dm2 = ancho.value * alto.value
    subTotal = (dm2 * (precioBase) * cant)
    total = subTotal
    if(mayorista==true){
      total = (dm2 * (pMayorista) * cant)
      desc.value = subTotal-total
    } else desc.value = 0
  }
  presu.value = total

}

const agregar = async () => {
    if(id_cliente == "" || id_cliente == null){
      $('#documento').focus();
      return 0;
    }
    if ($('#fecha_entrega').val() == ''){
      $('#fecha_entrega').focus()
      return 0
    }
    if($('#checkDelivery').is(':checked') == true  && $('#direccion').val() == ''){
      $('#direccion').focus()
      return 0
    }

    if($('#fecha_pedido').val() == ''){
      $('#fecha_pedido').focus()
      return 0
    }
    if(cantidad.value == 0 || cantidad.value == '' || cantidad.value < 0){
      $('#cantidad').focus();
      return 0;
    }
    if(codMetodo == 2 || codMetodo == 3){
      if($('#ancho').val() == '' || $('#ancho').val() == 0 || $('#ancho').val() < 0){
        $('#ancho').focus()
        return 0;
      }
      if($('#alto').val() == '' || $('#alto').val() == 0 || $('#alto').val() < 0){
        $('#alto').focus()
        return 0;
      }

    }
    
    $("#agregar").prop("disabled", true);
    if(band == false){
      let dataPedido = {
        "fecha":  document.getElementById('fecha_pedido').value,
        "cliente_id": id_cliente,
        "delivery": {
          'solicitado' : false
        }
      }
      if(checkDel.checked){
        dataPedido.delivery.solicitado = true
        dataPedido.delivery.direccion = $('#direccion').val()
      }
      console.log(dataPedido)
      codPedido = await create_pedido(dataPedido)
      console.log(codPedido)
      if(codPedido == 0){
        console.log("Error al Crear el Pedido");
        return 0;
      }
      CODPEDIDO = codPedido
      $('.codPedido').html(codPedido)
      band = true
    }
    // disabled the submit button
    //$("#btnSubmit").prop("disabled", true);
    
    if(FECHAENTREGA == null)
      FECHAENTREGA = document.getElementById("fecha_entrega").value
    var codProducto = $('#listaProductos :selected').val()
    let detPedido = {
      "codPedido": codPedido,
      "codProducto": codProducto,
      "medidas": {},
      "descripcion": document.getElementById("descripcion").value,
      "cantidad": cantidad.value,
      "fechaEntrega": FECHAENTREGA
    } 
    if(codMetodo == 2 || codMetodo == 3){
      detPedido.medidas = {
        "ancho": document.getElementById('ancho').value,
        "alto": document.getElementById('alto').value
      }
    }


    //falta enviar los detalle del pedido para que guarde en la base de datos
    //ya actualiza solo la tabla principal del pedido
    //aun falta hacer que upload actualice en la bd las rutas de los archivos
    //para eso habrá que enviarle el codigo de detalle del pedido  y el codigo del pedido
    //falta general el codigo del detalle de pedido
    detalle = await aggDetallePedido(detPedido);
    if(detalle == 0){
      return 0;
    }
    if (detalle.senaRequerida == true){
      $('#help').html('Se requiere de una seña del 50% como minimo para pasar los pedidos a producción')
    }
    console.log(detPedido);
    if(document.getElementById("archivos").value != ''){
      let form = document.getElementById("aggPedido")
      let data = new FormData(form);
      console.log(data)
      data.append("cod_pedido", codPedido);    
      data.append("cod_detalle", detalle.codDetalle);
      files = await uploadFiles(data);
      console.log(files)
    }else
      files = []
    

      
    actLista(detPedido.descripcion, detPedido.cantidad, files, detPedido.fechaEntrega, detalle.presu, detalle.codDetalle);
    
    SALDO = TOTAL = detalle.total
    $('.total').text(detalle.total)
    $("#terminar").prop("disabled", false);
    $('#fecha_pedido').prop('disabled', true)
    $("#agregar").prop("disabled", false);
    $("#documento").prop("disabled", true);
    $('#buscar').hide()
    $('#newCliente').hide()
    $('#divDocumento').addClass('col-sm-10')
    $('#descripcion').val('')
    $('#cantidad').val('')
    $('#archivos').val('')
    $('#presupuesto').val('')
    $('#descuento').val('')
    $('#ancho').val('')
    $('#alto').val('')
}

const cancelar = async () =>{
  //$('#cancelar').prop('disabled', true)
  if (CODPEDIDO != null){
    await eliminarPedido(CODPEDIDO)
  }
  

}

const agregarCliente = () =>{
  var documento = $('#newDocumento')
  var nombre = $('#newNombre')
  var apellido = $('#newApellido')
  if(documento.val()==''){
    documento.focus()
    return 0;
  }
  if(nombre.val()==''){
    nombre.focus()
    return 0;
  }
  if(apellido.val()==''){
    apellido.focus()
    return 0;
  }

  var data = {
    "documento": documento.val(),
    "nombre": nombre.val(),
    "apellido": apellido.val(),
    "email": $('#newEmail').val(),
    "celular":$('#newCelular').val(),
    "direccion": $('#newDireccion').val(),
    "nacionalidades_id": $('#newNacionalidad :selected').val()
  }
  
  $.ajax({
    type: "POST",
    url: "/clientes/agg/cliente",
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: 'json',
    success: function(result, textStatus, xhr) { 
        console.log(result)
        //document.getElementById("newCliente").reset()

    },
    success: function(xhr, textStatus) {
      console.log("success - "+textStatus)
      console.log(data.documento)
      $('#documento').val(data.documento);
      $('#alertNuevoCliente').html('')
      $('#newCliente-modal').modal('hide');
      get_client()

    },
    error: function(e){
      console.log(e.responseText)
      if(e.status == 409){
        $('#alertNuevoCliente').addClass('alert-danger')
        $('#alertNuevoCliente').html('El Cliente ya se encuentra Registrado')
      }
        
      if(e.status == 500){
        $('#alertNuevoCliente').addClass('alert-warning')
        $('#alertNuevoCliente').html('Ocurrió un error interno')
      }
        
    }
});
}

/*$('#checkDelivery').change(function (e){
  if($(this).is(':checked')){
    $('#divDireccion').show()
  }
  else
  $('#divDireccion').hide()
})/*/

$('#terminar').click(function(){
  if(BANDPRINT == false){
    $('#imprimirRecibo').hide()
    $('#imprimirFactura').hide()
  }

  $('#monto').attr({
      "max" : TOTAL,     
      "min" : 0       
  });
})



$('#imprimirResumen').click(function(){
  window.open(
    '/pedidos/resumen/'+CODPEDIDO,
    '_blank'
  );

})
$('#terminarPedido').click(function(){
  location.reload()
})

async function infoPedido(codDetalle){
  $('#abonar-div').prop('hidden', true)
  $('.abonar-btn').prop('hidden', false)
  $('#entregarPedido-btn').html('Entregar Pedido/s')
  $('#detallesPedido-div').prop('hidden', false)
  $('.changeInfo').prop('hidden', true)
  $('#alertPedidos').prop('hidden', true)
  document.getElementById("files").value = ''
  $('#btnEditar').show()
  $('#btnGuardar').prop('hidden', true)
  $('.infoPedido').prop('disabled', true)
  $('#infoArchivos').html('')
  $('#alto').val(0)
  $('#ancho').val(0)
  $('#detallePedido').modal('show')
  var detalle = await detallesPedido(codDetalle)
  CODDETALLE = detalle.codDetalle
  CODPEDIDO = detalle.codPedido
  id_cliente = detalle.cliente._id['$oid']
  console.log(detalle)

  if(detalle.produccionPedido.produccionTerminada == true)
    $('.entregar-btn').show()
  else
    $('.entregar-btn').hide()

  if(detalle.entrega.entregado == true){
    $('.entregar-btn').hide()
    $('#btnEditar').hide()
  }else{
    $('.entregar-btn').show()
    $('#btnEditar').show()
  }
  $('#infoCod').val(detalle.codPedido)
  $('#fecha_entrega').val(detalle.fechaEntrega)
  if(detalle.pedido.infoDelivery)
    $('#checkDelivery').prop('checked', detalle.pedido.infoDelivery.solicitado)
  if(detalle.pedido.infoDelivery.solicitado == true){
    $('.direccion').show()
    $('#direccion').val(detalle.pedido.infoDelivery.direccion)
  }else{
    $('.direccion').hide()
  }
  $('#infoProducto').val(detalle.producto.codProducto +' - '+ detalle.producto.descripcion)
  $('#infoDescripcion').val(detalle.descripcion)
  if(detalle.detalleProducto.metodoCalculo.codMetodo == 1){
    $('#dimensiones').hide()
  }else{
    $('#alto').val(detalle.detalleProducto.medidas.alto)
    $('#ancho').val(detalle.detalleProducto.medidas.ancho)
  }
  $('#infoCantidad').val(detalle.cantidad)
  $('#total').text(detalle.estadoCuenta.total)
  $('#saldo').html('<b>Saldo:</b> ' + detalle.estadoCuenta.saldo)
  if(detalle.estadoCuenta.saldo <= 0)
    $('.abonar-btn').prop('hidden', true)
  if(detalle.archivos != undefined){
    console.log('i')
    for(i in detalle.archivos){
        console.log(detalle.archivos[i].ruta)
        var newRow = $("<tr>");
        var cols = "";
        cols += '<td><a href="/files?ruta='+ detalle.archivos[i].ruta +'" target="_blank"> '+ detalle.archivos[i].nombre +"</a></td>";
        newRow.append(cols);
        cols = '<td><a name="" id="" class="btn btn-primary" href="/files/download?ruta='+ detalle.archivos[i].ruta +'&filename='+detalle.archivos[i].nombre+'" role="button"><i class="ri-download-2-line"></i></a> <button type="button" value='+ detalle.archivos[i].ruta +' onclick="eliminarArchivo('+"'"+ detalle.archivos[i].nombre + "', '"+ CODPEDIDO +"','"+ CODDETALLE+ "'" +')" class="btn btn-danger infoPedido" disabled><i class="ri-delete-bin-5-fill"></i></button></td>'
        newRow.append(cols);
        $("#infoArchivos").append(newRow);
    }
  }
}

$('#aggArchivo').click(async function(){
  if(document.getElementById("files").value != ''){
    let form = document.getElementById("formArchivos")
    let archivos = new FormData(form);
    archivos.append("cod_pedido", CODPEDIDO);    
    archivos.append("cod_detalle", CODDETALLE);
    console.log(archivos.get("cod_pedido"))
    console.log(archivos.get("cod_detalle"))
    console.log(archivos.get("files"))
    $("#aggArchivo").prop("disabled", true)
    files = await uploadFiles(archivos);
    $("#aggArchivo").prop("disabled", false)
    for(i in files){
        console.log(files[i])
        var newRow = $("<tr>");
        var cols = "";
        cols += '<td><a href="/files?ruta='+ files[i].ruta +'" target="_blank"> '  +files[i].nombre+"</a></td>";
        newRow.append(cols);
        cols = '<td><a name="" id="" class="btn btn-primary" href="/files/download?ruta='+ files[i].ruta +'&filename='+files[i].nombre+'" role="button"><i class="ri-download-2-line"></i></a> <button type="button" value='+ files[i].nombre +' onclick="eliminarArchivo('+ "'" + files[i].ruta + "', '"+ CODPEDIDO +"','"+ CODDETALLE+ "'" +')" class="btn btn-danger"><i class="ri-delete-bin-5-fill"></i></button></td>'
        newRow.append(cols);
        $("#infoArchivos").append(newRow);
    }
  }else
      files = []
  document.getElementById("files").value = ''
  })

$('#btnEditar').click(function(){
  $('.infoPedido').prop('disabled', false)
  $('#btnEditar').hide()
  $('#btnGuardar').prop('hidden', false)
})

function change(){
  if($('#checkDelivery').is(':checked') == true ){
    $('.direccion').show()
  }
  else{
    $('.direccion').hide()
  }
  if(CODPEDIDO == null)
    return 0
  $('#saveChange-btn').prop('hidden', false)
  $('.changeInfo').prop('hidden', false)
}
$('#checkDelivery, #fecha_entrega').change(function(){
  change()
})

$('#direccion').on('input',function(){
  change()
});

$('#saveChange-btn').click(function(){
  if(CODPEDIDO == null)
    return 0
  FECHAENTREGA = $('#fecha_entrega').val()
  if(FECHAENTREGA == ''){
    $('#fecha_entrega').focus()
    return 0
  }
  var datos = {
    delivery:{
      solicitado : $('#checkDelivery').is(':checked'),
      direccion : $('#direccion').val()
    },
    fechaEntrega : FECHAENTREGA
  }
  if(datos.delivery.solicitado == true && datos.delivery.direccion == ''){
    $('#direccion').focus()
    return 0
  }
  if( datos.delivery.solicitado != true ){
    datos.delivery.direccion = ''
  }
  actInfoPedido(CODPEDIDO, datos)
})

$('#btnGuardar').click(async function(){
  if(!CODDETALLE){
    alert('Ocurrió un error')
    return 0
  }
  var descripcion = $('#infoDescripcion')
  var cantidad = $('#infoCantidad')
  var medidas = {
    ancho : $('#ancho').val(),
    alto: $('#alto').val()
  }
  if(cantidad.val()<=0){
    cantidad.focus()
    return 0
  }
  datos ={
    codDetalle: CODDETALLE,
    codPedido: CODPEDIDO,
    descripcion: descripcion.val(),
    medidas: medidas,
    cantidad: cantidad.val()
  }
  var info = await editarDetalle(datos)
  $('#resultEdicion').html('<p><b>Presupuesto: </b>'+ info.presupuesto)
  $('#resultEdicion').prop('hidden', false)
  $('#btnGuardar').prop('hidden', true)
  $('#imprimirResumen').prop('hidden', false)
  $('.infoPedido').prop('disabled', true)


})



async function eliminarArchivo(filename, codPedido, codDetalle){
  await deleteArchivo(filename, codPedido, codDetalle)
  await infoPedido(codDetalle)
  $('.infoPedido').prop('disabled', false)
}

$('#entregarPedido-btn').click( async function(){
  $('#entregarPedido-btn').prop('disabled', true)
  $('#entregarPedido-btn').html('<i class="ri-check-double-fill"></i>')
  datos ={
    codPedido: CODPEDIDO
  }
  await entregarPedido(datos)
})

$('#abonarPedido-btn').click(async function(){
  $('#abonar-div').prop('hidden', false)
  $('#detallesPedido-div').prop('hidden', true)
  $('#btnEditar').prop('hidden', true)
  $('#btnGuardar').prop('hidden', true)
  await abonar(CODPEDIDO)
})

init()
prodSelected()
$('#listaProductos').change(prodSelected)
select.addEventListener("change", actPresup);
//select_var.addEventListener("change", varSelected);
//select_var.addEventListener("change", actPresup);
cantidad.addEventListener('input', actPresup)
agg.addEventListener('click', agregar)
aggCliente.addEventListener('click', agregarCliente)
//cantidad.addEventListener('input', desc)
//checkDel.addEventListener('input', actPresup)
cancel.addEventListener('click', cancelar)

