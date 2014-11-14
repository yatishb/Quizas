$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';
});

$('.list_option ul li').click(function() {
    
});