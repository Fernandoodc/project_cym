function login() {
    console.log('loin')
    data = {
        'username': document.getElementById('username').value,
        'password': document.getElementById('password').value
    }
    $.ajax({
        type: "POST",
        url: "/login/",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result, textStatus, xhr) { 
            console.log(result.msg)
            if(xhr.status == 202){
                div = document.getElementById('login_alert')
                div.innerHTML = ''
                div.setAttribute('class', '')
                window.location.href = '/index'
            }
        },
        complete: function(xhr, textStatus) {
            console.log(textStatus)
            if (xhr.status == 401){
                div = document.getElementById('login_alert')
                div.innerHTML = 'Usuario o Contraseña Incorrecta'
                div.setAttribute('class', 'alert alert-danger')
            }
        } 
    });
}