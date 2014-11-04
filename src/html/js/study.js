$(document).ready(function() {
    $('.grey_cover').hide();
    $('.button_container').hide();
    //document.getElementById('top_layer').style.display = "none";
});

$('.list_option ul li').on("tap", function() {
    //document.getElementById('top_layer').style.display = "block";
    $('.grey_cover').show();
    $('.button_container').show();
});

$('.grey_cover').on("tap", function() {
   $('.grey_cover').hide(); 
   $('.button_container').hide();
});

$('#quiz').on("tap", function(){
    window.location.href="singlePlayer.html";
});

$('#flashcard').on("tap", function(){
    window.location.href="flashcard.html";
});