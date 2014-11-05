// (function() {
//     var link = "singlePlayer.html";

//     $('.list_option ul li').click(function() {
//         //document.getElementById('top_layer').style.display = "block";
//         $('.study_button').show();
//         //window.location.href=link;
//     });
// })();

// function getStudySetContent(){
//     AjaxManager.prototype.GetContentBySetId();
// }
var content;

$(document).ready(function() {
    getStudySetContent();
});

$(document).ajaxComplete(function() {
    var element = $('.flashcards');
    for (var i = 0; i < content.cards.length; i++) {
        element.append(
            "<div class='simple_card' id='" +
            i +
            "'><div class='card_question'>" +
                content.cards[i].question +
                "</div><div class='card_answer'>" +
                content.cards[i].answer +
                "</div></div>"
        );
    };
});

function getStudySetContent(){
    $.get("/api/sets/quizlet:24957714", function(data) {
           content = JSON.parse(data);
           if(content != null)
               console.log("Set data have been fetched.");
           else
               console.log("Failed to fetch data.");
    })
     .fail(function() {
        alert("error in getStudySetContent call back function");
    });
}