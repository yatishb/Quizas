$(document).ready(function() {
    // $('.grey_cover').hide();
    // $('.button_container').hide();
});

$('.list_option ul li').on("click", function() {
    $('.button_container').show();
    $('.grey_cover').show();

    console.log("Button enabled.");
});

$('.grey_cover').on("click", function() {
    $('.grey_cover').hide(); 
    $('.button_container').hide();
   console.log("Button disabled.");
});

$('#quiz').on("tap", function(){
    window.location.href="singlePlayer.html";
});

$('#flashcard').on("tap", function(){
    window.location.href="flashcard.html";
});

$('#challenge').on("tap", function(){
    //window.location.href="challenge.html";
});