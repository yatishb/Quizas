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

        var existing_buttons = 3;
        var height = ['0px', '50px', '95px', '140px'];

        if(quizas_is_authorized_for("twitter")) {
            $('.login_button.twitter').hide();
            existing_buttons--;
        }
        if(quizas_is_authorized_for("quizlet")) {
            $('.login_button.quizlet').hide();
            existing_buttons--;
        }
        if(quizas_is_authorized_for("facebook")) {
            $('.login_button.facebook').hide();
            existing_buttons--;
        }

        $('.login_container').css('height', height[existing_buttons]);
    }
});

function logout_clear () {
    quizas_logout();
    document.location.href='index.html';
}