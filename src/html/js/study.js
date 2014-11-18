var content;
var next_page;
var pupup_mode;
var selected_set_id;
var selected_friend_id = "0";

$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';

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

    console.log(socket);

    // event handler for server sent data
    // the data is displayed in the "Received" section of the page
    socket.on('game request', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Request info is ")
        console.log(content);

        pupup_mode = "request";

        showPopup("User " + content.requestfrom + " is inviting you to compete set " + content.set);
    });

    // event handler for rejected request
    socket.on('game rejected', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Reject by ")
        console.log(content);

        pupup_mode = "rejected";

        showPopup("Your request was rejected by " + content.rejectedby);
    });

    // event handler for when user not online
    socket.on('user not online', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Reject by ")
        console.log(content);

        pupup_mode = "offline";

        showPopup("The user " + content.rejectedby + " is not online");
    });

    // event handler for when user does not exist
    socket.on('user non-existent', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Reject by ")
        console.log(content);

        pupup_mode = "non-existent";

        showPopup("The user " + content.rejectedby + " does not exist");
    });

    // event handler for accepted request
    socket.on('game accepted', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Accepted by ");
        console.log(content);

        pupup_mode = "accepted";

        socket.emit('disconnect');
        initializeMultiplayerGame(content);
    });
});

$('.notification').on("click", function() {
    getNotification();
    $('.grey_cover').show();
    $('.challenge_info').show();
    $('.challenge_info').addClass('fadeIn');
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

    console.log("selected_set_id is " + selected_set_id);
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

$('#practice').on("click", function(){
    next_page = "s";
    // $('.friend_window').show();
    // $('.friend_window').addClass('fadeIn');
    // $('.list_search').focus();
});

$('.friend_list').on("click", '.simple_friend', function () {
    $('.selected').removeClass('selected');
    $(this).addClass('selected');

    if($(this).parent().hasClass('list_online')) next_page = "q";
    else next_page = "c";

    selected_friend_id = this.id;

    console.log("selected_friend_id is " + selected_friend_id);
});

$('.list_bottom').on("click", function () {
    if (selected_friend_id=="0") {
        alert("Please select a friend");
        return;
    }

    if (next_page=="q") {
        // quiz with ONLINE friend
        console.log("namespace: "+namespace);
        console.log("socket: "+socket);
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

    console.log('rejected');
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

function showPopup(message) {
    if(pupup_mode == "request") {
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
    } else {
        $(document.body).append(
            "<div class='popup_window noselect'>" +
            "<div class='popup_message'><span>" +
            message +
            "</span></div>" +
            "<div class='popup_buttons'>" +
            "<div class='popup_button ok'>Ok</div>" +
            "</div></div>"
        );
    }
}

function initializeGame(friend_id, set_id, user_id) {
    sessionStorage.setItem("friend_id", JSON.stringify(friend_id));
    sessionStorage.setItem("set_id", JSON.stringify(set_id));
    sessionStorage.setItem("user_id", JSON.stringify(user_id));
    window.location.href="singlePlayer.html";
}

function initializeMultiplayerGame(content) {
    //win
    //encounter
    //encounterwin
    //total
    sessionStorage.setItem("initialization", JSON.stringify(content));
    window.location.href="example3.html";
}

function getSetContent() {
    $.get("/api/user/" + quizas_user_id() + "/sets", function(data) {
        var set_ids = JSON.parse(data);
        // console.log(set_ids);

        var sets = $('.set_info');
        sets.append("<div class='space'></div>");
        for (var i = 0; i < set_ids.length; i++) {
            $.get("/api/sets/" + set_ids[i], function(data) {
                var set_content = JSON.parse(data);

                sets.append(
                    "<div class='simple_set " +
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
        for (var i = 0; i < result.length; i++) {
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

        console.log(result);

        // var sets = $('.search_result');
        // for (var i = 0; i < result.length; i++) {
        //     sets.append(
        //         "<div class='simple_set search " +
        //         ("" + result[i].id).replace(":", "_") +
        //         "' id='" +
        //         result[i].id +
        //         "'><div class='content_container'>" +
        //         "<div class='set_content title search'><p>" +
        //         result[i].name + ' [' + result[i].size + ']' +
        //         "</div><div class='set_content description search'><p>" +
        //         result[i].description +
        //         "</div></div>" +
        //         "<div class='action_container'>" +
        //         "<div class='action add'><i class='fa fa-plus'></i></div>" +
        //         "</div></div>"
        //     );
        // }
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

function outputFriends(friends) {
    friends.forEach(function (f) {
        $('.list_online').append(
            "<div class='simple_friend " +
            ("" + f.userid).replace(":", "_") +
            "' id='" +
            f.userid +
            "'><div class='friend_profile'><img src='" +
            "'></div><span>" +
            f.name +
            "</span></div>"
        );

        quizas_get_profile_for(f.userid, function (p) {
            var address;

            address = p.picture;

            if (!address || address.length == 0 || address == undefined) {
                address = '../css/images/profile_default.png';
            }

            var newname = '.' + ("" + f.userid).replace(":", "_");
            $(newname).find('.friend_profile img').attr('src', address);
        });
    });

    console.log("finish friends");
}

function splitFriend(listOnlineUsers) {
    var offlineList = $('.list_offline');
    console.log("gets in here");

    $('.list_online .simple_friend').each(function() {
        var flag = false;
        var userid = $(this).attr('id');
        console.log("obtained friends");

        for (var i = 0; i < listOnlineUsers.length; i++) {
            console.log(listOnlineUsers[i]);
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