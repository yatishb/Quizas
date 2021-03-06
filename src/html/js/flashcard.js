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

    $('.top_bar div').html(content.name);

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
    }
});

function getStudySetContent(setid) {
    $.get("/api/sets/" + setid, function(data) {
           content = JSON.parse(data);
    })
     .fail(function() {
        alert("error in getStudySetContent call back function");
    });
}

$('.flashcards').on('click', '.simple_card', function() {
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