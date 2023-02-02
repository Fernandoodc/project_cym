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