$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';
});

$('.add_set').on('click', function() {
    location.href='createNewSet.html';
});

function logout_clear () {
    quizas_logout();
    document.location.href='index.html';
}

function outputProfile(profile) {
    $('.profile_photo img').attr('src', profile.picture);
    $('.name_content').text(profile.name);
}