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

$(document).ready(function() {
    var element = $('.flashcards');
    var content = getStudySetContent();
    for (var i = 0; i < content.length; i++) {
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
           var content = JSON.parse(data);
           console.log(content.cards[1].id);
           console.log(content.cards[1].question);
           console.log(content.cards[1].answer);
           return content;
           // $('.simple_card').attr("id",content.cards[1].id);
           // $('.card_question')[0].innerHTML = content.cards[1].question;
           // $('.card_answer')[0].innerHTML = content.cards[1].answer;
    })
     .fail(function() {
        alert("error in getStudySetContent call back function");
    });
}