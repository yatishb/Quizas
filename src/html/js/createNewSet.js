var signed_in;

$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0) {
        $('.back_button').hide();
        signed_in = 0;
    } else {
        signed_in = 1;
    }
});

$('.back_button').on("click", function() {
    document.location.href='/settings.html';
});

$('.create').on("click", function() {
    $('.page_create').show();
    $('.page_main').hide();
    $('.page_container').addClass('v_type');
    $('body,html').css('overflow','visible');

    if (signed_in) {
        $('.not_sign_in').hide();
    }
});

$('.upload').on("click", function() {
    $('.page_upload').show();
    $('.page_main').hide();
    $('.page_container').addClass('v_upload');
    $('body,html').css('overflow','visible');

    if (signed_in) {
        $('.not_sign_in').hide();
    }
});

$('.finish').on("click", function() {
    $('.page_main').show();
    $('.page_upload').hide();
    $('.page_create').hide();
    $('.page_container').removeClass('v_upload');
    $('.page_container').removeClass('v_type');
    $('.page_container').addClass('v_original');
    $('body,html').css('overflow','hidden');
});

$('.cancel').on("click", function() {
    $('.page_main').show();
    $('.page_upload').hide();
    $('.page_create').hide();
    $('.page_container').removeClass('v_upload');
    $('.page_container').removeClass('v_type');
    $('.page_container').addClass('v_original');
    $('body,html').css('overflow','hidden');
});

$('.upload').on("click", function() {
   $("#upload").trigger('click');
});

$('.finish').on("click", function() {
   $("#finish").trigger('click');
});