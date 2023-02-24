function verificarPaswLen(){
    var newPaw = $('#newPasw').val()
    if(newPaw.length < 6){
        $('#newPasw').css('border-color', '#dc3545');
        $('#alertPaswLen').prop('hidden', false)
        return false
    }else{
        $('#newPasw').css('border-color', '');
        $('#alertPaswLen').prop('hidden', true)
        return true
    }
}
function verificarPaswEq(){
    var newPaw = $('#newPasw').val()
    var reNewPasw = $('#reNewPasw').val()
    if( newPaw !=  reNewPasw){
        $('.newPasw').css('border-color', '#dc3545');
        $('#alertnewPasw').prop('hidden', false)
        return false
    }
    else{
        $('.newPasw').css('border-color', '');
        $('#alertnewPasw').prop('hidden', true)
        return true
    }
}


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

$('#changePassword').submit(async function (e) { 
    e.preventDefault();
    if(verificarPaswEq == false || verificarPaswLen() == false)
        return 0
    var datos = {
        currentPasw : $('#currentPassword').val(),
        newPasw : $('#newPasw').val(),
    }
    await changePassword(datos)
    $('#changePasw-btn').html('<i class="ri-check-double-line"></i>');
    $('#newPasw').val('')
    $('#reNewPasw').val('')
    $('#currentPassword').val('')

});

