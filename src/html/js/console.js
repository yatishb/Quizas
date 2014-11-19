function displayContent() {
    $.get("/api/leaderboard", function (data) {
        // Obj is of format:
        // obj = { data: [{ id: "facebook:xyzw..", points: # }] }
        var obj = JSON.parse(data);
        leaderboard = obj.data;
        console.log(obj);

        // Clear all children DOM elements from leaderboard,
        // so we don't have any mess.
        var leaderboardContainer = $('#board_container');
        leaderboardContainer.empty();

        for (i = 0; i < leaderboard.length; i++) {
            var rank = i + 1;
            var userid = leaderboard[i].id;
            var fbid = userid.substring("facebook:".length);
            var pic = "http://graph.facebook.com/" + fbid + "/picture?type=square";
            var points = leaderboard[i].points;
            var extraClass = " ";

            // 1st, 2nd, 3rd get extra DOM class
            if (1 <= rank && rank <= 3) {
                extraClass = ["first", "second", "third"][rank - 1];
            }

            // For-each row in the leaderboard,
            //  add a row div with a profile img, a div for name, and a score.
            // Then, callback and update the divs with the name and img.
            var rowEl = $("<div/>", { class: 'simple_leader' }).appendTo(leaderboardContainer);
            $("<div/>", { class: 'rank font-effect-shadow-multiple ' + extraClass })
                .appendTo(rowEl).text(rank);
            var profileImg =
                $("<img/>").appendTo($("<div/>", { class: "profile" })
                                     .appendTo(rowEl))
            var profileNameDiv =
                $("<div/>", { class: "name" }).appendTo(rowEl);

            $("<div/>", { class: "score" }).appendTo(rowEl).text(points);


            // Due to nature of closures,
            // we need to ensure our callback refers to the correct
            // variable!
            // (n.b. a leaderboard.forEach(function (r) { ... }) wouldn't suffer this).
            var updateProfileCallback = (function(nameDiv, profileImg) {
                return function(profile) {
                    // profile = { name, picture }
                    console.log("callback");
                    nameDiv.text(profile.name);
                    profileImg.attr("src", profile.picture);
                };
            })(profileNameDiv, profileImg);

            // Get profile data, update the row <img/> and <div/> with these.
            quizas_get_profile_for(userid, updateProfileCallback);
        }
    });
}

// function getName() {
//     console.log($('.simple_leader'));
//     $('.simple_leader').each(function() {
//         var userid = $(this).find('.name').text();
//         if(userid.indexOf('facebook:') >= 0) {
//             quizas_get_profile_for(userid, function(profile) {
//                 var element = $(this).find('.name');
//                 element.text(profile.name);
//                 element.attr('title', profile.name);
//             });
//         }
//     });
// }
