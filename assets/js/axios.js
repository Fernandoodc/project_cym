function get_client() {
    console.log('gg')
    doc = document.getElementById('documento').value
        $.ajax({
            type: "GET",
            url: "/get_client/?doc="+doc,
            
            success: function(result, textStatus, xhr) { 
                console.log(result)
                if(xhr.status == 200){
                    console.log("econtro")
                    document.getElementById('nombre').value=result.nombre + " " + result.apellido
                    document.getElementById('numCelular').value = result.celular
                    document.getElementById('direccion').value = result.direccion
                }
            },
            complete: function(xhr, textStatus) {
                if(xhr.status == 404){
                    document.getElementById('nombre').value= ""
                    document.getElementById('numCelular').value = ""
                    document.getElementById('direccion').value = ""
                }
            } 
        });
    
}

function get_products(){
        $.ajax({
            type: "GET",
            url: "/get_client/?doc="+doc,
            
            success: function(result, textStatus, xhr) { 
                console.log(result)
                document.getElementById('nombre').value=result.nombre + " " + result.apellido
                document.getElementById('numCelular').value = result.celular
                document.getElementById('direccion').value = result.direccion

            },
            complete: function(xhr, textStatus) {
            } 
        });
    
}
