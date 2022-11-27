const select = document.getElementById('productos')
//const select_var = document.getElementById('variaciones')
const cantidad = document.getElementById('cantidad')
const checkDel = document.getElementById("checkDelivery")
const agg = document.getElementById("agregar")
const aggCliente = document.getElementById("aggCliente")
let codMetodo = 0
precioBase = 0
precioExtra = 0
precio = 0
descuento = 0
band = false
//let variaciones = []
var pMayoristas = []
id_cliente = ""
function init(){
  var fPedido = document.getElementById("fecha_pedido")
  var fEntrega = document.getElementById("fecha_entrega")
  fPedido.value = date(1)
  fPedido.setAttribute("min", date(1))
  fEntrega.value = date()
  fEntrega.setAttribute("min", date())
}

function date(format=2){
  var f = new Date() 
  var year = f.getFullYear()
  var month = f.getMonth()+1
  if(f.getDate()<10){
    day = "0"+f.getDate()
  }
  else{
    day = f.getDate()
  
  }
  if(f.getMinutes()<10){
    min = "0"+f.getMinutes();
  }
  else{
    min = f.getMinutes();
  }
  if (format == 1){
    return(year+"-"+month+"-"+day)
  }
  return(year+"-"+month+"-"+day +"T"+f.getHours()+":"+min)
}

const prodSelected = () => {
    let indice = select.selectedIndex;
    if(indice === -1) return;
    console.log(indice)
    console.log(productos[indice])
    //variaciones = productos[indice].variaciones
    pMayoristas = productos[indice].preciosMayoristas
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
  if(!checkDel.checked){
    var deliv = 0
    //console.log("no check")
  }
  else var deliv = delivery
  //console.log(deliv)
  
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
        subTotal = (cant * (precioBase)) + deliv
        total = subTotal
        if(mayorista==true){
          total = (cant * (pMayorista)) + deliv
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
    subTotal = (dm2 * (precioBase) * cant) + deliv
    total = subTotal
    if(mayorista==true){
      total = (dm2 * (pMayorista) * cant) + deliv
      desc.value = subTotal-total
    } else desc.value = 0
  }
  presu.value = total

}




const agregar = async () => {
    if(id_cliente == ""){
      $('#documento').focus();
      return 0;
    }
    if(cantidad.value == 0 || cantidad.value == ''){
      $('#cantidad').focus();
      return 0;
    }
    if(band == false){
      let dataPedido = {
        "fecha":  document.getElementById('fecha_pedido').value,
        "cliente_id": id_cliente
      }
      console.log(dataPedido)
      codPedido = await create_pedido(dataPedido)
      if(codPedido == 0){
        console.log("Error al Crear el Pedido");
        return 0;
      }
      band = true
    }
    
    // disabled the submit button
    //$("#btnSubmit").prop("disabled", true);
    
    let detPedido = {
      "codPedido": codPedido,
      "codProducto": select.value,
      "medidas": {},
      "descripcion": document.getElementById("descripcion").value,
      "cantidad": cantidad.value,
      "fechaEntrega": document.getElementById("fecha_entrega").value,
      "delivery": false
    } 
    if(checkDel.checked){
      detPedido.delivery = true
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
    
      
    actLista(detPedido.descripcion, detPedido.cantidad, files, detPedido.fechaEntrega, detPedido.delivery, detalle.presu, detalle.codDetalle);

}
/*function getFiles()
{
	var idFiles=document.getElementById("archivos");
	// Obtenemos el listado de archivos en un array
	var archivos=idFiles.files;
	// Creamos un objeto FormData, que nos permitira enviar un formulario
	// Este objeto, ya tiene la propiedad multipart/form-data
	var data=new FormData();
	// Recorremos todo el array de archivos y lo vamos añadiendo all
	// objeto data
	for(var i=0;i<archivos.length;i++)
	{
		// Al objeto data, le pasamos clave,valor
		data.append("archivo"+i,archivos[i]);
	}
	return data;
}
 
/**
 * Función que recorre todo el formulario para apadir en el FormData los valores del formulario
 * @param string id hace referencia al id del formulario
 * @param FormData data hace referencia al FormData
 * @return FormData
 */
/*function getFormData(id,data)
{
	$("#"+id).find("input,select").each(function(i,v) {
        if(v.type!=="file") {
            if(v.type==="checkbox" && v.checked===true) {
                data.append(v.name,"on");
            }else{
                data.append(v.name,v.value);
            }
        }
	});
	return data;
}*/

const agregarCliente = () =>{
  data = {
    "documento": document.getElementById("newDocumento").value,
    "nombre": document.getElementById("newNombre").value,
    "apellido": document.getElementById("newApellido").value,
    "email": document.getElementById("newEmail").value,
    "celular": document.getElementById("newCelular").value,
    "direccion": document.getElementById("newDireccion").value
  }
  
  console.log(data)
  
  $.ajax({
    type: "POST",
    url: "/agg/clients",
    data: JSON.stringify(data),
    contentType: "application/json",
    dataType: 'json',
    success: function(result, textStatus, xhr) { 
        console.log(result)
        //document.getElementById("newCliente").reset()

    },
    complete: function(xhr, textStatus) {
    } 
});
}


/*{
  "fecha":,
  "cliente_id":,
  "detallesPedido":[
    "detalleProducto":{
      "producto_id":,
      "medidas":
    },
    "cantidad":
    "delivery":
    "descripcion":
    "fechaHoraEntrega":
    "archivos": 
  ]
}*/

/*const desc = () => {
  pMayorista = 0
  precio = precioBase
  for(i=0; i<pMayoristas.length; i++){
    if(cantidad.value>=pMayoristas[i].cantidad)
      pMayorista = pMayoristas[i].precio
  }
  const divDesc = document.getElementById("descuento")
  divDesc.innerHTML = ""
  if(pMayorista>0){
    divDesc.setAttribute("class", "row mb-3")
    const labelDesc = document.createElement("label")
    labelDesc.setAttribute("class", "col-sm-2 col-form-label")
    labelDesc.innerHTML = "Descuento"
    const divIDesc = document.createElement("div")
    divIDesc.setAttribute("class", "col-sm-10")
    const inputDesc = document.createElement("input")
    inputDesc.disabled = true
    inputDesc.setAttribute("class", "form-control")
    inputDesc.setAttribute("type", "number")
    divDesc.appendChild(labelDesc)
    divIDesc.appendChild(inputDesc)
    divDesc.appendChild(divIDesc)
  }
}*/
//console.log(date())
init()
prodSelected()
select.addEventListener("change", prodSelected);
select.addEventListener("change", actPresup);
//select_var.addEventListener("change", varSelected);
//select_var.addEventListener("change", actPresup);
cantidad.addEventListener('input', actPresup)
agg.addEventListener('click', agregar)
aggCliente.addEventListener('click', agregarCliente)
//cantidad.addEventListener('input', desc)
checkDel.addEventListener('input', actPresup)

