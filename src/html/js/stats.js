$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';

    $('.list_search input').on('input', function() {
        var search_txt = $(this).val();

        $('.simple_friend.invite').each(function() {
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

    getUserStats();
});

$('.stats_tab').on('click', function() {
    if(!$(this).hasClass('current_tab'))
    {
        $(this).parent().find('.current_tab').removeClass('current_tab');
        $(this).addClass('current_tab');
    }

    if($(this).text() == "Myself") {
        $('.page_me').show();
        $('.page_friend').hide();
        $('.friendTitle').empty();
        $('.chartContainer').empty();
        $('.friendTable').empty();
        $('.friend_stats').hide();
        $('.grey_cover').hide();
        $('.friend_window').hide();
    } else {
        $('.page_me').hide();
        $('.page_friend').show();
    }
});

$('.page_friend').on('click', '.simple_friend', function() {
    var friend_id = $(this).attr('id');

    $('.friendTitle').empty();
    $('.chartContainer').empty();
    $('.friendTable').empty();
    
    $('.friend_stats').show();
    $('.friend_stats').addClass('fadeIn');
    $('.chartContainer').append('<canvas class="friendChart"></canvas>');
    getFriendStats(friend_id);
    // test();
});

$('.page_me').on('click', '.game_button', function() {
    if(!$(this).hasClass('active')) {
        $('.game_button.active').removeClass('active');
        $(this).addClass('active');
        
        var gameid = $(this).attr('id');
        $('#line_graph_me').empty();
        outputStatsForGame(quizas_user_id(), gameid, 'line_graph_me');
    }
});

$('.page_friend').on('click', '.game_button.friend', function() {
    if(!$(this).hasClass('active')) {
        $('.game_button.active').removeClass('active');
        $(this).addClass('active');
        
        var gameid = $(this).attr('id');
        $('#line_graph_friend').empty();
        outputStatsForGame(quizas_user_id(), gameid, 'line_graph_friend');
    }
});

$(document).on('click', '.button_close', function() {
    $('.friendTitle').empty();
    $('.chartContainer').empty();
    $('.friendTable').empty();
    $('.friend_stats').hide();
});

$(document).on('click', '.invite_friend', function() {
    $('.grey_cover').show();
    $('.friend_window').show();
    $('.friend_window').addClass('fadeIn');
    $('.list_search').focus();
    // get all friends
});

$('.grey_cover').on('click', function() {
    $(this).hide();
    $('.friend_window').hide();
});

function getUserStats() {
    var userid = quizas_user_id();

    $.get("/api/user/" + userid + "/stats", function(data) {
        var result = JSON.parse(data);

        if(result.played == 0) {
            $('.chartTitle').append("No statistics to show!<br><span style='color:red'>START PLAYING!</span>");
        } else {
            $('.game_details.me').show();
            $('.myChart').show();
            $('.graphTable.me').show().css('display', 'table');

            $('.chartTitle').append("Your statistics!<br><span style='color:red'>Play MORE!</span>");

            var data = [
                {
                    value: result.wins,
                    color:"#F7464A",
                    highlight: "#FF5A5E",
                    label: "Wins"
                },
                {
                    value: result.draws,
                    color: "#46BFBD",
                    highlight: "#5AD3D1",
                    label: "Draws"
                },
                {
                    value: result.losses,
                    color: "#FDB45C",
                    highlight: "#FFC870",
                    label: "Losses"
                }
            ];

            // Get context with jQuery - using jQuery's .get() method.
            var ctx = $(".myChart").get(0).getContext("2d");

            // For a pie chart
            window.myNewChart = new Chart(ctx).Pie(data);
        }

        $('.chartTable').append(
            "<tr><td>Total</td><td class='number'>" +
            result.played +
            "</td><td class='block white'></tr>" +
            "<tr><td>Wins</td><td class='number'>" +
            result.wins +
            "</td><td class='block red'></td></tr>" +
            "<tr><td>Draws</td><td class='number'>" +
            result.draws +
            "</td><td class='block green'></td></tr>" +
            "<tr><td>Losses</td><td class='number'>" +
            result.losses +
            "</td><td class='block yellow'></td></tr>"
        );
    })
    .fail(function() {
        console.log("error in getUserStats function");
    });

    // TODO: In order to add linegraphs / barcharts,, you should..
    //  i) for each graph you want, have a div
    //     (each with a unique ID. See `quizas_gamestats_linegraph.js`).
    //  ii) call outputStatsForGame(userid, gameid, graphDivId)
    //
    //  The biggest problem you will face is that the SIZE of
    //  the graph will be fucked up.
    //  See the relevant `quizas_gamestats_*.js` files.
    //  Might have to modify functions. NOTE that barchart
    //  height should be dependent on # of words in the flashset.


    // Line Graphs for Each Game the user has played.
    // (A Combo Box to select a particular game would make
    //  more sense).
    $.get("/api/user/" + userid + "/stats/games", function (data) {
        //$("#line_graph_me").text(data);
        // Call on for-each game.
        var response = JSON.parse(data);
        
        var j = 1;
        var extraClass= " ";
        response.forEach(function (gameId) {
            if (j == 1) extraClass = 'active';
            else extraClass = ' ';
            $('.game_buttons.me').append(
                "<div class='game_button " +
                extraClass +
                "' id='" +
                gameId +
                "'>" +
                j +
                "</div>"
            );
            j++;
        });

        if(response != "") {
            outputStatsForGame(userid , response[0], 'line_graph_me');
        }
    });
}

function getFriendStats(friend_id) {
    var userid = quizas_user_id();

    $.get("/api/user/" + userid + "/stats/vs/" + friend_id, function(data) {
        var result = JSON.parse(data);

        // var result = {wins: 5, draws: 3, losses: 2, total: 10};

        if(result.played == 0) {
            $('.friendTitle').append("No statistics to show!<br><span style='color:red'>START PLAYING!</span>");
        } else {
            $('.friendChart').show();

            $('.friendTitle').append("Your statistics!<br><span style='color:red'>Play MORE!</span>");

            var data = [
                {
                    value: result.wins,
                    color:"#F7464A",
                    highlight: "#FF5A5E",
                    label: "Wins"
                },
                {
                    value: result.draws,
                    color: "#46BFBD",
                    highlight: "#5AD3D1",
                    label: "Draws"
                },
                {
                    value: result.losses,
                    color: "#FDB45C",
                    highlight: "#FFC870",
                    label: "Losses"
                }
            ];

            // Get context with jQuery - using jQuery's .get() method.
            var ctx = $(".friendChart").get(0).getContext("2d");

            // For a pie chart
            window.myNewChart = new Chart(ctx).Pie(data);
        }

        $('.friendTable').append(
            "<tr><td>Total</td><td class='number'>" +
            result.played +
            "</td><td class='block white'></tr>" +
            "<tr><td>Wins</td><td class='number'>" +
            result.wins +
            "</td><td class='block red'></td></tr>" +
            "<tr><td>Draws</td><td class='number'>" +
            result.draws +
            "</td><td class='block green'></td></tr>" +
            "<tr><td>Losses</td><td class='number'>" +
            result.losses +
            "</td><td class='block yellow'></td></tr>"
        );

        for(var i = 0; i < result.commongames.length; i++) {
            var extraClass = ' ';
            var number = i + 1;
            if(number == 1) extraClass = 'active';
            else extraClass = ' ';
            $('.game_buttons.friend').append(
                "<div class='game_button " +
                extraClass +
                "' id='" +
                gameId +
                "'>" +
                number +
                "</div>"
            );
        }

        if(result.played > 0) {
            $('.game_details.friend').show();
            $('.graphTable.friend').show().css('display', 'table');
            outputStatsForGame(userid , result.commongames[0], 'line_graph_friend');
        }
    })
    .fail(function() {
        console.log("error in getFriendStats function");
    });
}

function outputFriends(friends) {
    friends.forEach(function (f) {
        $('.page_friend').append(
            "<div class='simple_friend stats " +
            ("" + f.userid).replace(":", "_") +
            "' id='" +
            f.userid +
            "'><div class='friend_profile stats'><img src='" +
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

    // $('.page_friend').append("<div class='invite_friend'>Invite Friends</div>");
}
