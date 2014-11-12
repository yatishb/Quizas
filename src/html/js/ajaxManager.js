function AjaxManager() {

}

AjaxManager.prototype.GetContentBySetId = function (onSuccess, SetId) {
    $.ajax({
        type: 'GET',
        url: '/api/sets/',
        data: 'quizlet:24957714',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
        success: function(data) {
            var content = JSON.parse(data);
            console.log(content.cards[1].id);
            console.log(content.cards[1].question);
            console.log(content.cards[1].answer);
            $('.simple_card').attr("id",content.cards[1].id);
            $('.card_question').innerHTML = content.cards[1].question;
            $('.card_answer').innerHTML = content.cards[1].answer;
        }.fail(function() {
            alert("Error in getStudySetContent call back function");
        });
    });
}