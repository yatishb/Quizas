$(document).ready(function() {
});

$('.create').on("click", function() {
//$('.create').click(function() {
    $('.page_create').show();
    $('.page_main').hide();
    $('.page_container').addClass('v_type');
    $('body,html').css('overflow','visible');
});

$('.upload').on("click", function() {
    $('.page_upload').show();
    $('.page_main').hide();
    $('.page_container').addClass('v_upload');
    $('body,html').css('overflow','visible');
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