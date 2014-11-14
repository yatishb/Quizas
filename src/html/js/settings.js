$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';
});

$('.create_set').on('click', function() {
    location.href='createNewSet.html';
});

$('.add_sns').on('click', function() {
    if ($('.login_container').is(':visible')) {
        $('.login_container').hide();
        $(this).removeClass('clicked');
    } else {
        $('.login_container').show();
        $(this).addClass('clicked');
    }
});

function logout_clear () {
    quizas_logout();
    document.location.href='index.html';
}