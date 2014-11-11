var set_ids;
var content;
var next_page;
var selected_set_id;
var selected_friend_id = "0";

$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';

    $('body,html').css('overflow','visible');
    $('body,html').css('overflow-x','hidden');

    getSetContent();

    $('.list_search input').on('input', function() {
        var search_txt = $(this).val();
        console.log(search_txt);

        $('.simple_friend').each(function() {
            var this_friend = $(this);
            if(search_txt == "") {
                this_friend.show();
            } else {
                if(this_friend.find('span').text().toUpperCase().indexOf(search_txt.toUpperCase()) == -1) {
                    this_friend.hide();
                }
            }
        });
    });

    listFacebookFriends(outputFriends);
});

//$('.list_option ul li').on("click", function() {
$('.simple_set').on("click", function() {
    $('.add_set').hide();
    $('.button_container').show();
    $('.grey_cover').show();

    selected_set_id = this.id;

    console.log("selected_set_id is " + selected_set_id);
});

$('.grey_cover').on("click", function() {
    if ($('.friend_window').is(':visible')) {
        $('.friend_window').hide();
    } else {
        $('.grey_cover').hide(); 
        $('.button_container').hide();
        $('.add_set').show();
    }
});

$('#quiz').on("tap", function(){
    next_page = "q";
    $('.friend_window').show();
    //window.location.href="singlePlayer.html";
});

$('#flashcard').on("tap", function(){
    window.location.href="flashcard.html";
});

$('#challenge').on("tap", function(){
    //window.location.href="challenge.html";
    next_page = "c";
    $('.friend_window').show();
});

$('.simple_friend').on("click", function () {
    $('.selected').removeClass('selected');
    $(this).find('.friend_profile').addClass('selected');

    selected_friend_id = this.id;

    console.log("selected_friend_id is " + selected_friend_id);
});

$('.list_bottom').on("click", function () {
    if (selected_friend_id=="0") {
        alert("Please select a friend");
        return;
    }

    console.log("The next page is " + next_page);

    if (next_page=="q") window.location.href="singlePlayer.html";
    else if (next_page=="c") window.location.href="#";
    else alert("error in starting game");
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

function outputFriends(friends) {
    friends.forEach(function (f) {
        $('.friend_list').append(
            "<div class='simple_friend' id='" +
            f.userid +
            "'><div class='friend_profile'><img src='" +

            "'></div><span>" +
            f.name +
            "</span></div>"
        );
    });
}