var content;
var cardIndex;
var cardPerPage = 10;

$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';

    var address = document.URL;

    var setid = address.substring(address.indexOf("=")+1, address.length);
    
    getStudySetContent(setid);

    $(window).scroll(function() {
        if($(window).scrollTop() == $(document).height() - $(window).height()) {
            var flashcards = $('.flashcards');

            if (content != null) {
                for (var i = 0; i < content.cards.length && i < cardPerPage; i++) {
                    flashcards.append(
                        "<div class='simple_card' id='" +
                        cardIndex +
                        "'><div class='flipper'><div class='card_content question'><span>" +
                            content.cards[cardIndex].question +
                            "</span></div><div class='card_content answer'><span>" +
                            content.cards[cardIndex].answer +
                            "</span></div></div></div>"
                    );
                    cardIndex++;
                }
            }
        }
    });
});

$(document).ajaxComplete(function() {
    cardIndex = 0;

    var top_bar = $('.top_bar');
    top_bar.html(content.name);

    var flashcards = $('.flashcards');
    for (var i = 0; i < content.cards.length && i < cardPerPage; i++) {
        flashcards.append(
            "<div class='simple_card' id='" +
            cardIndex +
            "'><div class='flipper'><div class='card_content question'><span>" +
                content.cards[cardIndex].question +
                "</span></div><div class='card_content answer'><span>" +
                content.cards[cardIndex].answer +
                "</span></div></div></div>"
        );

        cardIndex++;

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
    }
});

function getStudySetContent(setid) {
    $.get("/api/sets/" + setid, function(data) {
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

$('.flashcards').on('click', '.simple_card', function() {
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

$('.back_button').on("click", function(){
    window.location.href="study.html";
});