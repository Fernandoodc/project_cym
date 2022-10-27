const select = document.getElementById('productos')
const select_var = document.getElementById('variaciones')
const cantidad = document.getElementById('cantidad')
const checkDel = document.getElementById("checkDelivery")
const agg = document.getElementById("agregar")
const aggCliente = document.getElementById("aggCliente")
let codMetodo = 0
precioBase = 0
precioExtra = 0
precio = 0
descuento = 0
let variaciones = []
pMayoristas = []

const prodSelected = () => {
    let indice = select.selectedIndex;
    if(indice === -1) return;
    console.log(indice)
    console.log(productos[indice])
    variaciones = productos[indice].variaciones
    pMayoristas = productos[indice].preciosMayoristas
    select_var.innerHTML=""
    console.log(variaciones.length)
    for(i=0; i<variaciones.length ; i++){
      option = document.createElement('option')
      option.text=variaciones[i].descripcion
      option.value=variaciones[i].codVariacion
      select_var.appendChild(option)
    }
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
const varSelected = () => {
  let indice = select_var.selectedIndex;
  if(indice===-1) return;
  precioExtra = variaciones[indice].precioExtra

}

const actPresup = () => {
  pMayorista = 0
  mayorista = false
  //console.log("actProd")
  const presu = document.getElementById("presupuesto")
  const cant = document.getElementById("cantidad").value
  const desc = document.getElementById("descuento")
  if(!checkDel.checked){
    deliv = 0
    //console.log("no check")
  }
  else deliv = delivery
  //console.log(deliv)
  
  for(i=0; i<pMayoristas.length; i++){
    console.log(pMayoristas[i].cantidad)
    console.log(cant)
    if(cant>=pMayoristas[i].cantidad){

      pMayorista = pMayoristas[i].precio
      mayorista = true
      //console.log(mayorista + " : " + pMayorista)
    }
  }

  if(codMetodo==0) return;
  else
    if(codMetodo==1){
        subTotal = (cant * (precioBase + precioExtra)) + deliv
        total = subTotal
        if(mayorista==true){
          total = (cant * (pMayorista + precioExtra)) + deliv
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
    subTotal = (dm2 * (precioBase + precioExtra) * cant) + deliv
    total = subTotal
    if(mayorista==true){
      total = (dm2 * (pMayorista + precioExtra) * cant) + deliv
      desc.value = subTotal-total
    } else desc.value = 0
  }
  presu.value = total

}

const agregar = () => {
    data=getFiles();
    data=getFormData("aggPedido",data);
    console.log(data)
    /*$.ajax({
        url:"/agregar_pedido",
        type:"POST",
        data: data,
        dataType:"json",
        contentType:false,
        processData:false,
        cache:false
    }).done(function(data){
        alert(data)
    });*/
}
function getFiles()
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
function getFormData(id,data)
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
}

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
        document.getElementById("newCliente").reset()

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

prodSelected()
select.addEventListener("change", prodSelected);
select.addEventListener("change", actPresup);
select_var.addEventListener("change", varSelected);
select_var.addEventListener("change", actPresup);
cantidad.addEventListener('input', actPresup)
agg.addEventListener('click', agregar)
aggCliente.addEventListener('click', agregarCliente)
//cantidad.addEventListener('input', desc)
checkDel.addEventListener('input', actPresup)