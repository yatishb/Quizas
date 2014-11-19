var content;
var next_page;
var popup_mode;
var myname;
var myurl;
var selected_set_id;
var selected_set_name;
var selected_friend_id = "0";

$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';

    $('body,html').css('overflow-x','hidden');

    getSetContent();

    $('.list_search input').on('input', function() {
        var search_txt = $(this).val();

        $('.simple_friend').each(function() {
            var this_friend = $(this);
            if(search_txt == "") {
                this_friend.show();
            } else {
                if (this_friend.find('span').text().toUpperCase().indexOf(search_txt.toUpperCase()) == -1) {
                    this_friend.hide();
                } else {
                    this_friend.show();
                }
            }
        });
    });

    /*namespace = '/test'; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    socket = io.connect('http://' + document.domain + ':' + location.port + namespace, {
                                "connect timeout": 300,
                                "close timeout": 30,
                                "hearbeat timeout": 30
                            });*/

    // event handler for server sent data
    // the data is displayed in the "Received" section of the page
    socket.on('game request', function(msg) {
        content = JSON.parse(msg.data);

        popup_mode = "request";

        showPopup(content.requestfrom, content.set);
        // showPopup("User " + content.requestfrom + " is inviting you to compete set " + content.set);
    });

    // event handler for rejected request
    socket.on('game rejected', function(msg) {
        content = JSON.parse(msg.data);

        popup_mode = "rejected";

        showPopup(content.rejectedby,"nothing");
        // showPopup("Your request was rejected by " + content.rejectedby);
    });

    // event handler for when user not online
    socket.on('user not online', function(msg) {
        content = JSON.parse(msg.data);

        pupup_mode = "offline";

        showPopup(content.rejectedby, "nothing");
        // showPopup("The user " + content.rejectedby + " is not online");
    });

    // event handler for when user does not exist
    socket.on('user non-existent', function(msg) {
        content = JSON.parse(msg.data);

        pupup_mode = "non-existent";

        showPopup(content.rejectedby,"nothing");
    });

    // event handler for accepted request
    socket.on('game accepted', function(msg) {
        content = JSON.parse(msg.data);

        pupup_mode = "accepted";
        
        quizas_get_profile_for(content.enemyID, function (p) {
            var newInit = {
                playerName: myname,
                playerSprite: myurl,
                playerPoints: content.playerPoints,
                /*playerWin: content.playerWin,
                playerTotal: content.playerTotal,*/
                enemyName: p.name,
                enemySprite: p.picture,
                enemyPoints: content.enemyPoints,
                /*enemyWin: content.enemyWin,
                enemyTotal: content.enemyTotal,*/
                encounterTotal: content.encounterTotal,
                encounterWin: content.encounterWin,
                matchName: content.matchName,
                totalQuestions: content.totalQuestions,
                room: content.room
            };
            
            socket.emit('disconnect');
            initializeMultiplayerGame(newInit);
        });
    });
});

$('.notification').on("click", function() {
    getNotification();
    $('.grey_cover').show();
    $('.challenge_info').show();
    $('.challenge_info').addClass('fadeIn');
});

$('.challenge_info').on('click', '.simple_info', function() {
    var element = $(this).find('.action_set');
    if(element.is(':visible')) {
        element.hide();
    } else {
        element.show();
        element.addClass('stretchLeft');
    }
});

$('.friend_window .button_close').on("click", function() {
    $('.friend_window').hide();
});

$('.challenge_info .button_close').on("click", function() {
    $('.grey_cover').hide();
    $('.challenge_info').hide();
});

$('.set_info').on("click", '.content_container', function() {
    $('.search_set').hide();
    $('.search_result').hide();
    $('.add_set i').removeClass('rotate');
    $('.button_container').show();
    $('.grey_cover').show();

    selected_set_id = $(this).parent().attr('id');
    selected_set_name = $(this).find('.set_content p').text();
});

$('.set_info').on("click", '.favorite', function() {
    var id = $(this).parent().attr('id');
    var flag = true;

    if($(this).children().hasClass('fa-star-o')) {
        $(this).empty();
        $(this).append("<i class='fa fa-star'></i>");
    } else {
        flag = false;
        $(this).empty();
        $(this).append("<i class='fa fa-star-o'></i>");    
    }

    var result = favoriteSet(id,flag);
});

$('.set_info').on("click", '.delete', function() {
    var id = $(this).parent().parent().attr('id');

    deleteSet(id);
});

$('.search_result').on("click", '.add', function() {
    var id = $(this).parent().parent().attr('id');
    addSet(id);
});

$('.add_set').on("click", function() {
    if ($('.search_set').is(':visible')) {
        $(this).find('i').removeClass('rotate');
        $('.search_set').removeClass("slideLeft");
        $('.search_set').hide();
        $('.search_result').hide();
        $('.set_info').show();
        $('.set_info').empty();
        getSetContent();
    } else {
        $(this).find('i').addClass('rotate');
        // $('.set_info').hide();
        $('.search_set').show();
        $('.search_set').addClass("slideLeft");
        $('#search_set_box').focus();
    }
});

$('#search_set_box').keypress(function( event ) {
    if ( event.which == 13 ) {
        var search_txt = $(this).val();

        $('.search_result').empty();

        if (search_txt || search_txt != "") {
            $('.set_info').hide();
            $('.search_result').show();
            getSearchResult(search_txt);
        } else {
            $('.search_result').empty();
        }
    }
});

$('.grey_cover').on("click", function() {
    if ($('.challenge_info').is(':visible')) {
        $('.challenge_info').hide();
        $(this).hide();
    } else if ($('.friend_window').is(':visible')) {
        $('.friend_window').hide();
        $('.friend_window').removeClass('fadeIn');
    } else {
        $('.grey_cover').hide();
        $('.button_container').hide();
        $('.add_set').show();
        $('.notification').show();
    }
});

$('#flashcard').on("click", function(){
    link = 'flashcard.html?setid=' + selected_set_id;
    window.location.href = link;
});

$('#challenge').on("click", function(){
    // Get the list of online users
    socket.emit('online users');
    socket.on('online', function(msg) {
        var listOnlineUsers = msg.data;
        splitFriend(listOnlineUsers);
    });

    $('.friend_window').show();
    $('.friend_window').addClass('fadeIn');
    $('.list_search').focus();


});

function getUserPicture() {
    quizas_get_profile(function(profile) {
        myname = profile.name;
        myurl = profile.picture;
        console.log(myurl);
    });
}

$('#practice').on("click", function(){
    next_page = "s";

    initializePracticeGame(selected_set_id, quizas_user_id());
});

$('.friend_list').on("click", '.simple_friend', function () {
    $('.selected').removeClass('selected');
    $(this).addClass('selected');

    if($(this).parent().hasClass('list_online')) next_page = "q";
    else next_page = "c";

    selected_friend_id = this.id;
});

$('.list_bottom').on("click", function () {
    if (selected_friend_id=="0") {
        alert("Please select a friend");
        return;
    }

    if (next_page=="q") {
        // quiz with ONLINE friend
        socket.emit('send notification', {
            'opponent': selected_friend_id,
            'set': selected_set_id,
            'user': quizas_user_id()
        });
    } else if (next_page=="c") {
        // challenge with OFFLINE friend
        initializeGame(selected_friend_id, selected_set_id, quizas_user_id());
    }
});


$(document.body).on("click", '.popup_button.cancel', function() {
    $('.popup_window').remove();

    socket.emit('reject', {
        'requester': content.requestfrom,
        'receiver': quizas_user_id()
    });
});

$(document.body).on("click", '.popup_button.accept', function() {
    $('.popup_window').remove();

    socket.emit('assignroom', {
        'user1': content.requestfrom,
        'flashset': content.set,
        'user2': quizas_user_id()
    });
});

$(document.body).on("click", '.popup_button.ok', function() {
    $('.popup_window').remove();
});

function showPopup(userid, setid) {
    // request  rejected  offline  non-existent  accepted
    if(popup_mode == "request") {
        quizas_get_profile_for(userid, function (p) {
            var message = "User " + p.name + " is inviting you to compete set " + setid;
            $(document.body).append(
                "<div class='popup_window noselect'>" +
                "<div class='popup_message'><span>" +
                message +
                "</span></div>" +
                "<div class='popup_buttons'>" +
                "<div class='popup_button cancel'>Reject</div>" +
                "<div class='popup_button accept'>Accept</div>" +
                "</div></div>"
            );
        });
    } else {
        quizas_get_profile_for(userid, function (p) {
            if(popup_mode == "rejected") message = "Your request was rejected by " + p.name;
            else if(popup_mode == "offline") message = "The user " + p.name + " does not exist";
            else if(popup_mode == "non-existent") message = "The user " + p.name + " is not online";

            $(document.body).append(
                "<div class='popup_window noselect'>" +
                "<div class='popup_message'><span>" +
                message +
                "</span></div>" +
                "<div class='popup_buttons'>" +
                "<div class='popup_button ok'>Ok</div>" +
                "</div></div>"
            );
        });
    }
}

function initializeGame(friend_id, set_id, user_id) {
    sessionStorage.setItem("friend_id", JSON.stringify(friend_id));
    sessionStorage.setItem("set_id", JSON.stringify(set_id));
    sessionStorage.setItem("user_id", JSON.stringify(user_id));
    window.location.href="challenge.html";
}

function initializeMultiplayerGame(content) {
    //win
    //encounter
    //encounterwin
    //total
    console.log(content);
    sessionStorage.setItem("initialization", JSON.stringify(content));
    window.location.href="example3.html";
}

function initializePracticeGame(set_id, user_id) {
    sessionStorage.setItem("set_id", JSON.stringify(set_id));
    sessionStorage.setItem("user_id", JSON.stringify(user_id));
    window.location.href="singlePlayer.html";
}

function getSetContent() {
    $.get("/api/user/" + quizas_user_id() + "/sets", function(data) {
        var set_ids = JSON.parse(data);

        var sets = $('.set_info');
        sets.append("<div class='space top'></div>");
        for (var i = 0; i < set_ids.length; i++) {
            if(set_ids[i]=="undefined") continue;
            $.get("/api/sets/" + set_ids[i], function(data) {
                var set_content = JSON.parse(data);

                var additionalClass = "";
                if(i==(set_ids.length-1)) additionalClass="last ";

                sets.append(
                    "<div class='simple_set " +
                    additionalClass +
                    ("" + set_content.id).replace(":", "_") +
                    "' id='" +
                    set_content.id +
                    "'><div class='content_container'>" +
                    "<div class='set_content title'><p>" +
                    set_content.name +
                    "</div></div>" +
                    "<div class='action_container'>" +
                    "<div class='action favorite'><i class='fa fa-star-o'></i></div>" +
                    "<div class='action delete'><i class='fa fa-trash-o'></i></div>" +
                    "</div></div>"
                );
            });
        };
    })
    .fail(function() {
        console.log("error in getSetContent call back function");
    });
}

function getSearchResult(txt) {
    $.get("/api/sets/search/" + txt, function(data) {
        var result = JSON.parse(data);

        var sets = $('.search_result');
        sets.append("<div class='space top'></div>");
        for (var i = 0; i < result.length; i++) {
            // var additionalClass = "";
            // if(i==(result.length-1)) additionalClass="last ";
            sets.append(
                "<div class='simple_set search " +
                ("" + result[i].id).replace(":", "_") +
                "' id='" +
                result[i].id +
                "'><div class='content_container'>" +
                "<div class='set_content title search'><p>" +
                result[i].name + ' [' + result[i].size + ']' +
                "</div><div class='set_content description search'><p>" +
                result[i].description +
                "</div></div>" +
                "<div class='action_container'>" +
                "<div class='action add'><i class='fa fa-plus'></i></div>" +
                "</div></div>"
            );
        }

        $('.simple_set.search').each(function() {
            var containerHeight = $(this).height();
            var plusButton = $(this).find('.action_container');
            
            plusButton.css('height', containerHeight);
        });
    })
    .fail(function() {
        console.log("error in getSearchResult call back function");
    });
}

function getNotification() {
    var userid = quizas_user_id();

    $.get("/api/user/" + userid + "/challenges/", function(data) {
        var result = JSON.parse(data);
        var result_pending = result.pending;
        var result_done = result.done;

        if (result_pending.length > 0) {
            $('.notice_bubble').show().text(result_pending.length);
        }

        var list_pending = $('.info_pending');
        var list_done = $('.info_done');
        for (var i = 0; i < result_pending.length; i++) {
            quizas_get_profile_for(
                    result_pending[i].receipientUserId,
                    function(profile) {
                        var message = result_pending[i].receipientUserId + ' has challenged you on ' + result_pending[i].setName;
                        list_pending.append(
                            "<div class='simple_info id='" +
                            result_pending[i].setId +
                            "' name='" +
                            profile.name +
                            "'>" +
                            "<div class='info_content'><span>" +
                            message +
                            "</span></div>" +
                            "<div class='action_set'>" +
                            "<div class='button_accept'><i class='fa fa-check fa-2x'></i></div>" +
                            "<div class='button_reject'><i class='fa fa-plus rotate fa-2x'></i></div>" +
                            "</div></div>"
                        );
            });
        }

        for (var i = 0; i < result_done.length; i++) {
            quizas_get_profile_for(
                    result_pending[i].receipientUserId,
                    function(profile) {
                        var message = result_pending[i].receipientUserId + ' has completed ' + result_pending[i].setName;
                        list_done.append(
                            "<div class='simple_info id='" +
                            result_pending[i].setId +
                            "' name='" +
                            profile.name +
                            "'>" +
                            "<div class='info_content'><span>" +
                            message +
                            "</span></div>" +
                            "<div class='action_set'>" +
                            "<div class='button_accept'><i class='fa fa-check fa-2x'></i></div>" +
                            "<div class='button_reject'><i class='fa fa-plus rotate fa-2x'></i></div>" +
                            "</div></div>"
                        );
            });
        }
    })
    .fail(function() {
        console.log("error in getNotification call back function");
    });
}

function addSet(id) {
    var userid = quizas_user_id();

    // NOTE: For this to work, (i.e. to find the Set ID which should be added),
    // it's assumed that the add button is grandchild of the
    // <div id="quizlet:.." /> div.

    $.ajax({
        url: '/api/user/' + userid + '/sets/' + id,
        type: 'PUT',
        success: function() {
            var thisClass = ("" + id).replace(":", "_");
            $('.' + thisClass).remove();
        }
    });
}

function deleteSet(id) {
    var userId = quizas_user_id();

    $.ajax({
        url: '/api/user/' + userId + '/sets/' + id,
        type: 'DELETE',
        success: function() {
            var thisClass = ("" + id).replace(":", "_");
            $('.' + thisClass).remove();
        }
    });
}

function favoriteSet(id, flag) {
    
}

function splitFriend(listOnlineUsers) {
    var offlineList = $('.list_offline');

    $('.list_online .simple_friend').each(function() {
        var flag = false;
        var userid = $(this).attr('id');

        for (var i = 0; i < listOnlineUsers.length; i++) {
            if(userid == listOnlineUsers[i]) flag = true;
        }

        if(flag == false) {
            username = $(this).find('span').text();
            profileURL = $(this).find('img').attr('src');
            $(this).remove();
            offlineList.append(
                "<div class='simple_friend " +
                userid.replace(":", "_") +
                "' id='" +
                userid +
                "'><div class='friend_profile'><img src='" +
                profileURL +
                "'></div><span>" +
                username +
                "</span></div>"
            );
        }
    });
}