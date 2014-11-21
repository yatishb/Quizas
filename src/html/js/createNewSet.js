var signed_in;
var currentNumber;

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

$('.add_button.v_upload').on("click", function() {
    $('.content_area.v_upload').append(
        "<label><span>Question " +
        currentNumber +
        " :</span>" +
        "<input id='q" +
        currentNumber +
        "' type='text' name='question' placeholder='Type Your Question'/></label>" +
        "<label><span>Answer " +
        currentNumber +
        " :</span>" +
        "<input id='a" +
        currentNumber +
        "' type='text' name='answer' placeholder='Type Your Answer'/></label>"
    );

    currentNumber++;
});

$('.add_button.v_create').on("click", function() {
    $('.content_area.v_create').append(
        "<label><span>Question " +
        currentNumber +
        " :</span>" +
        "<input id='q" +
        currentNumber +
        "' type='text' name='question' placeholder='Type Your Question'/></label>" +
        "<label><span>Answer " +
        currentNumber +
        " :</span>" +
        "<input id='a" +
        currentNumber +
        "' type='text' name='answer' placeholder='Type Your Answer'/></label>"
    );

    currentNumber++;
});

$('.create').on("click", function() {
    $('.page_create').show();
    $('.page_main').hide();
    $('.page_container').addClass('v_type');
    $('body,html').css('overflow','visible');

    currentNumber = 3;

    if (signed_in) {
        $('.not_sign_in').hide();
    }

    $('.content_area.v_create').empty();
    $('.content_area.v_create').append(
        "<label><span>Question 1 :</span><input id='q1' type='text' name='question' placeholder='Type Your Question'/></label>" +
        "<label><span>Answer 1 :</span><input id='a1' type='text' name='answer' placeholder='Type Your Answer'/></label>" +
        "<label><span>Question 2 :</span><input id='q2' type='text' name='question' placeholder='Type Your Question'/></label>" +
        "<label><span>Answer 2 :</span><input id='a2' type='text' name='answer' placeholder='Type Your Answer'/></label>"
    );
});

$('.upload').on("click", function() {
    $('.page_upload').show();
    $('.page_main').hide();
    $('.page_container').addClass('v_upload');
    $('body,html').css('overflow','visible');

    currentNumber = 3;

    if (signed_in) {
        $('.not_sign_in').hide();
    }

    $('.content_area.v_upload').empty();
    $('.content_area.v_upload').append(
        "<label><span>Question 1 :</span><input id='q1' type='text' name='question' placeholder='Type Your Question'/></label>" +
        "<label><span>Answer 1 :</span><input id='a1' type='text' name='answer' placeholder='Type Your Answer'/></label>" +
        "<label><span>Question 2 :</span><input id='q2' type='text' name='question' placeholder='Type Your Question'/></label>" +
        "<label><span>Answer 2 :</span><input id='a2' type='text' name='answer' placeholder='Type Your Answer'/></label>"
    );
});

$('.finish').on("click", function() {
    $("#finish").trigger('click');

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