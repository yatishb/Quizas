var set_ids;
var content;
var next_page;
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
                if(this_friend.find('span').text().toUpperCase().indexOf(search_txt.toUpperCase()) == -1) {
                    this_friend.hide();
                }
            }
        });
    });

    namespace = '/test'; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    socket = io.connect('http://' + document.domain + ':' + location.port + namespace, {
                                "connect timeout": 300,
                                "close timeout": 30,
                                "hearbeat timeout": 30
                            });

    console.log("socket: "+socket);

    // event handler for server sent data
    // the data is displayed in the "Received" section of the page
    socket.on('game request', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Request info is ")
        console.log(content);

        var result;
        if (confirm("User " + content.requestfrom + " is inviting you to compete set " + content.set) == true) {
            socket.emit('assignroom', {
                'user1': content.requestfrom,
                'flashset': "quizlet:39748410",
                'user2': quizas_user_id()
            });
            /*socket.emit('assignroom', {
                'user1': content.requestfrom,
                'flashset': content.set,
                'user2': quizas_user_id()
            });*/
        } else {
            socket.emit('reject', {
                'requester': scontent.requestfrom,
                'receiver': quizas_user_id()
            });
        }
    });

    // event handler for rejected request
    socket.on('game rejected', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Reject by ")
        console.log(content);

        alert("Your request was rejected by " + content.rejectedby);
    });

    // event handler for when user not online
    socket.on('user not online', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Reject by ")
        console.log(content);

        alert("The user " + content.rejectedby + " is not online");
    });

    // event handler for when user does not exist
    socket.on('user non-existent', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Reject by ")
        console.log(content);

        alert("The user " + content.rejectedby + " does not exist");
    });

    // event handler for accepted request
    socket.on('game accepted', function(msg) {
        content = JSON.parse(msg.data);
        console.log("Accepted by ");
        console.log(content);

        initializeMultiplayerGame(content);
    });
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

    if (next_page=="q") {
        console.log("namespace: "+namespace);
        console.log("socket: "+socket);
        socket.emit('send notification', {
            'opponent': selected_friend_id,
            'set': selected_set_id,
            'user': quizas_user_id()
        });

    }

    // if (next_page=="q") window.location.href="singlePlayer.html";
    // else if (next_page=="c") window.location.href="#";
    // else alert("error in starting game");
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

function initializeGame(content) {
    //win
    //encounter
    //total
    window.location.href="singlePlayer.html";
}

function initializeMultiplayerGame(content) {
    //win
    //encounter
    //encounterwin
    //total
    sessionStorage.setItem("initialization", content);
    sessionStorage.setItem("socket", socket);
    window.location.href="example3.html";
}

function getSetContent() {
    $.get("/api/user/" + quizas_user_id() + "/sets", function(data) {
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