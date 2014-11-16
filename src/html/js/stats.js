$(document).ready(function() {
    var result = quizas_authorized_sites();
    if(result.length == 0)
        this.location.href='/index.html';

    var data = [
        {
            value: 300,
            color:"#F7464A",
            highlight: "#FF5A5E",
            label: "Win"
        },
        {
            value: 50,
            color: "#46BFBD",
            highlight: "#5AD3D1",
            label: "Draw"
        },
        {
            value: 100,
            color: "#FDB45C",
            highlight: "#FFC870",
            label: "Lose"
        }
    ];

    // Get context with jQuery - using jQuery's .get() method.
    var ctx = $(".myChart").get(0).getContext("2d");

    // For a pie chart
    window.myNewChart = new Chart(ctx).Pie(data);

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
    } else {
        $('.page_me').hide();
        $('.page_friend').show();
    }
});

function getUserStats() {
    var userid = quizas_user_id();

    $.get("/api/user/" + userid + "/stats", function(data) {
        var result = JSON.parse(data);
        console.log(result);
    })
    .fail(function() {
        console.log("error in getUserStats function");
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
}