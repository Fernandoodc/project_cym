cont = 0
function actLista(desc, cant, files, fechaE, presu, codDetalle){
    formBody = document.getElementById("bodyLista");
    formTr = document.createElement("tr");
    formTh = document.createElement("th");
    formDesc = document.createElement("td")
    formCant = document.createElement("td")
    formArch = document.createElement("td")
    formFech = document.createElement("td")
    formPresu = document.createElement("td")
    formBtns = document.createElement("td")

    formTh.innerHTML = cont+1;
    cont++;
    formDesc.innerHTML = desc;
    formCant.innerHTML = cant;
    let auxnom = "<p>";
    for(let i = 0 ; i < files.length; i++){
        //formArch.appendChild(files[i].nombre)
        auxnom = auxnom + files[i].nombre + "<br>"
    }
    formArch.innerHTML = auxnom + "</p>"
    formFech.innerHTML = fechaE;
    formPresu.innerHTML = presu;
    btnEdit = document.createElement('button');
    btnEdit.setAttribute("class", "btn btn-primary");
    btnEdit.setAttribute("onclick", "editarDet('"+ codDetalle +"')");
    btnEdit.innerHTML = '<i class="ri-edit-box-line"></i>';

    btnDel = document.createElement("button");
    btnDel.setAttribute("class", "btn btn-danger");
    btnDel.setAttribute("onclick", "eliminarDet('"+ codDetalle +"')");
    btnDel.innerHTML = '<i class="ri-delete-bin-5-line"></i>'
    //formBtns.appendChild(btnEdit);
    formBtns.appendChild(btnDel);

    formTr.appendChild(formTh);
    formTr.appendChild(formDesc)
    formTr.appendChild(formCant);
    formTr.appendChild(formArch);
    formTr.appendChild(formFech);
    formTr.appendChild(formPresu);
    formTr.appendChild(formBtns);
    formTr.setAttribute('id', codDetalle)
    formBody.appendChild(formTr);

}

