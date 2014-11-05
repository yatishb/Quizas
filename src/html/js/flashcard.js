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
    var top_bar = $('.top_bar');
    top_bar.html(content.name);

    var flashcards = $('.flashcards');
    for (var i = 0; i < content.cards.length; i++) {
        flashcards.append(
            "<div class='simple_card' id='" +
            i +
            "'><div class='flipper'><div class='card_content question'><p class='text_field'>" +
                content.cards[i].question +
                "</div><div class='card_content answer'><p>" +
                content.cards[i].answer +
                "</div></div></div>"
        );
    };
});

function getStudySetContent() {
    $.get("/api/sets/quizlet:24957714", function(data) {
           content = JSON.parse(data);
           console.log(content);
           if(content != null)
               console.log("Set data have been fetched.");
           else
               console.log("Failed to fetch data.");
    })
     .fail(function() {
        alert("error in getStudySetContent call back function");
    });
}

$('.flashcards').on('tap', '.simple_card', function() {
    // var cardID= this.id;
    // var card = $('#'+cardID).find('.flipper');
    //this.classList.toggle('hover');
    var card = $(this).find('.flipper');
    if(card.hasClass('flipped')) {
        card.removeClass('flipped');
    } else {
        card.addClass('flipped');
    }
});

$('.back_button').on("tap", function(){
    window.location.href="study.html";
});