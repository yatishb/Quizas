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
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';
    
    getStudySetContent();
});

$(document).ajaxComplete(function() {
    var top_bar = $('.top_bar');
    top_bar.html(content.name);

    var flashcards = $('.flashcards');
    var wait = 0;
    for (var i = 0; i < content.cards.length; i++) {
        flashcards.append(
            "<div class='card' id='" +
            i +
            "'><div class='flip'><div class='card_c'><p class='t_field'>" +
                content.cards[i].question +
                "</div><div class='card_c'><p>" +
                content.cards[i].answer +
                "</div></div></div>"
        );
        // if (i>0 && i%10 == 0)
        //     wait = 10000;
        // else wait = 0;

        // setTimeout(function(content){
        //     console.log(content);
        //     flashcards.append(
        //         "<div class='simple_card' id='" +
        //         i +
        //         "'><div class='flipper'><div class='card_content question'><p class='text_field'>" +
        //             content.cards[i].question +
        //             "</div><div class='card_content answer'><p>" +
        //             content.cards[i].answer +
        //             "</div></div></div>"
        //     );
        // }, wait);
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