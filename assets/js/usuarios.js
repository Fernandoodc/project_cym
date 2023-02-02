USERID = ''

async function infoUser(id){
    $('#newPasw').val('');
    $('#reNewPasw').val('');
    $('#alertnewPasw').prop('hidden', true)
    $('.newPasw').css('border-color', '');
    $('#newType-ok').prop('hidden', true)
    $('#newPasw-ok').prop('hidden', true)
    $('#alertPaswLen').prop('hidden', true)
    await $.ajax({
        type: "GET",
        url: "/usuarios/info?"+ $.param({"id": id}),
        success: function(result, textStatus, xhr) { 
            USERID = result._id['$oid']
            $('#editar-btn').prop('hidden', false)
            $('#guardarCambios-btn').prop('hidden', true)
            $('#alertUsername').prop('hidden', true)
            $('.obli').prop('hidden', true)
            $('.infoUser').prop('disabled', true)
            $('#editar-btn').prop('hidden', false)
            $('#newUsername').val(result.username);
            $('#documento').val(result.documento);
            $('#nombre').val(result.nombre);
            $('#apellido').val(result.apellido);
            $('#celular').val(result.celular);
            $('#nacionalidad').val(result.Nacionalidades_id).change()
            $('#email').val(result.email);
            $('#direccion').val(result.direccion);
            $('#typeUser').val(result.tipoUsuario.codTipo).change();
            $('#infoUser-modal').modal('show')
        },
        complete: function(xhr, textStatus){
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
}

$('#editar-btn').click(function (e) { 
    e.preventDefault();
    $('.infoUser').prop('disabled', false)
    $('#editar-btn').prop('hidden', true)
    $('#guardarCambios-btn').prop('hidden', false)
    $('.obli').prop('hidden', false)
});
$('#eliminarUser').click(function (e) { 
    e.preventDefault();
    $('#infoUser-modal').modal('hide')
    $('#eliminarUser-modal').modal('show')
});
$('#eliminar-btn').click(async function (e) { 
    e.preventDefault();
    $('#eliminar-btn').prop('disabled', true)
    await $.ajax({
        type: "DELETE",
        url: "/usuarios/eliminar?"+$.param({'id': USERID}),
        success: function(result, textStatus, xhr) { 
            $('#'+USERID).remove();
            $('#eliminarUser-modal').modal('hide')
        },
        complete: function(xhr, textStatus){
            $('#eliminar-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
});

$('#guardarCambios-btn').click(async function (e) { 
    $('#newUsername').css('border-color', '');
    e.preventDefault();
    var username = $('#newUsername')
    var documento = $('#documento')
    var nombre = $('#nombre')
    var apellido = $('#apellido')
    var nacionalidad = $('#nacionalidad :selected')
    if(username.val() == ''){
        username.focus()
        return 0
    }
    if(documento.val() == ''){
        documento.focus
        return 0
    }
    if(nombre.val() == ''){
        nombre.focus()
        return 0 
    }
    if(apellido.val() == ''){
        apellido.focus()
        return 0
    }
    if(nacionalidad.val() == ''){
        nacionalidad.focus()
    }
    var datos = {
        username: username.val(),
        documento: documento.val(),
        nombre: nombre.val(),
        apellido: apellido.val(),
        celular : $('#celular').val(),
        Nacionalidades_id: nacionalidad.val(),
        email: $('#email').val(),
        direccion: $('#direccion').val(),
    }
    console.log(datos)
    $('#guardarCambios-btn').prop('disabled', true)
    await $.ajax({
        type: "PUT",
        url: "/usuarios/editar?"+$.param({'id': USERID}),
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            infoUser(USERID)
        },
        complete: function(xhr, textStatus){
            $('#guardarCambios-btn').prop('disabled', false)
        },
        error: function(e){
            console.log(e)
            if(e.status == 409){
                $('#alertUsername').prop('hidden', false)
                $('#newUsername').css('border-color', '#dc3545');
            }else
                alert(e.statusText)
        }
    });

});
$('#newUsername').keyup(function (e) { 
    e.preventDefault();
    var newUsername = $('#newUsername').val()
    setTimeout(async () => {
        await $.ajax({
            type: "GET",
            url: "/usuarios/verif_username?"+ $.param({"username": newUsername, 'id': USERID}),
            success: function(result){
                $('#alertUsername').prop('hidden', true)
                $('#newUsername').css('border-color', '');
            },
            error: function(e){
                console.log(e)
                if(e.status == 409){
                    $('#alertUsername').prop('hidden', false)
                    $('#newUsername').css('border-color', '#dc3545');
                }else
                    alert(e.statusText)
            }
        })
    }, 1500);

});

$('#guardarTypeUser-btn').click(async function (e) { 
    e.preventDefault();
    $(this).prop('disabled', true)
    $('#newType-ok').prop('hidden', true)
    var typeUser = $('#typeUser :selected')
    if(typeUser.val() == ''){
        typeUser.focus()
        return 0
    }
    await $.ajax({
        type: "PUT",
        url: "/usuarios/change_type_user?"+ $.param({"newTypeUser": typeUser.val(), 'idUser': USERID}),
        success: function(result){
            $('#newType-ok').prop('hidden', false)
        },
        complete: function(xhr, textStatus){
            $('#guardarTypeUser-btn').prop('disabled', false);  
        },
        error: function(e){
            console.log(e)
            if(e.status == 409){
                $('#alertUsername').prop('hidden', false)
                $('#newUsername').css('border-color', '#dc3545');
            }
            else
                alert(e.statusText)
        }
    })
});

$('#reNewPasw, #newPasw').keyup(function (e) { 
    setTimeout(() => {
        if($('#reNewPasw').val() == ''){
            $('.newPasw').css('border-color', '');
            $('#alertnewPasw').prop('hidden', true)
            return 0
        }
        verificarPaswEq()
    }, 1000);
});
$('#newPasw').keyup(function (e) { 
    setTimeout(() => {
        verificarPaswLen()
    }, 500);
});

$('#changePasw-btn').click(async function (e) { 
    e.preventDefault();
    if(verificarPaswLen == false || verificarPaswEq() == false){
        return 0
    }
    $(this).prop('disabled', true)
    var datos ={
        userId: USERID,
        newPassword : $('#newPasw').val()
    }
    await $.ajax({
        type: "PUT",
        url: "/usuarios/reset_password",
        data: JSON.stringify(datos),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            $('#newPasw').val('')
            $('#reNewPasw').val('')
            $('#newPasw-ok').prop('hidden', false)
        },
        complete: function(xhr, textStatus){
            $('#changePasw-btn').prop('disabled', false);
            
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
});
$('#form-newUSer').submit(async function (e) { 
    e.preventDefault();
    if(verificarPaswLen == false || verificarPaswEq() == false){
        return 0
    }
    $(this).prop('disabled', true)
    var data = {
        username : $('#newUsername').val(),
        password: $('#newPasw').val(),
        codTipoUsuario : $('#typeUser :selected').val(),
        documento: $('#documento').val(),
        nombre: $('#nombre').val(),
        apellido: $('#apellido').val(),
        celular: $('#celular').val(),
        Nacionalidades_id: $('#nacionalidad :selected').val(),
        email: $('#email').val(),
        direccion: $('#direccion').val(),
    }
    console.log(data)
    await $.ajax({
        type: "POST",
        url: "/usuarios/new_user",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr){
            $('#newUser-ok').prop('hidden', false)
            location.reload
        },
        complete: function(xhr, textStatus){
            $('#form-newUSer').prop('disabled', true)
            
        },
        error: function(e){
            console.log(e)
            alert(e.statusText)
        }
    });
});


