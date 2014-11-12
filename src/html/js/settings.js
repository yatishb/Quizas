$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';
});

function logout_clear () {
    quizas_logout();
    document.location.href='index.html';
}