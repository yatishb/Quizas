var set_ids;
var content;

$(document).ready(function() {
    // $('.grey_cover').hide();
    // $('.button_container').hide();
    getSetContent();
});

//$('.list_option ul li').on("click", function() {
$('.simple_set').on("click", function() {
    $('.add_set').hide();
    $('.button_container').show();
    $('.grey_cover').show();

    console.log("Button enabled.");
});

$('.grey_cover').on("click", function() {
    $('.grey_cover').hide(); 
    $('.button_container').hide();
    $('.add_set').show();
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

$(document).ajaxComplete(function() {
    if(set_ids == null) return;
    
    var sets = $('.set_info');
    for (var i = 0; i < set_ids.length; i++) {
        // sets.append(
        //     "<div class='simple_set' id='" +
        //     i +
        //     "'><div class='set_content title'><p>" +
        //         set_ids.cards[i].question +
        //         "</div><div class='set_content description'><p>" +
        //         set_ids.cards[i].answer +
        //         "</div></div>"
        // );
    };
});

function getSetContent() {
    $.get("/api/user/quizlet:li_yuanda/sets", function(data) {
           set_ids = JSON.parse(data);
           console.log(set_ids);
           if(set_ids != null)
               console.log("Set data is empty.");
           else
               console.log("Failed to fetch data.");
    })
     .fail(function() {
        alert("error in getSetContent call back function");
    });
}