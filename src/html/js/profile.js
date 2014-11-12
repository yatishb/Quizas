$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';
});

$('.back_button').on("click", function() {
    document.location.href='/settings.html';
});

function outputProfile(profile) {
   // $("#profile").html("<b>" + profile.name + "</b><br/><img src='" + profile.picture + "' />");
}