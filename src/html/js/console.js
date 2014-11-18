$(document).ready(function() {
		setInterval(displayContent, 60000);
});

function displayContent() {
		$.get("/api/leaderboard", function (data) {
				var obj = JSON.parse(data);
				leaderboard = obj.data;
				console.log(obj);
			
				var element = $('.board_container');
				element.empty();

				for (i = 0; i < leaderboard.length; i++) {
						var rank = i + 1;
						var userid = leaderboard[i].id;
						var id = userid.substring(9);
						var pic = "http://graph.facebook.com/" + id + "/picture?type=square";
						var points = leaderboard[i].points;
						var extraClass = " ";

						if(i == 1) extraClass = "first";
						else if(i == 2) extraClass = "second";
						else if(i == 3) extraClass = "third";

						quizas_get_profile_for(userid, function(profile) {
								console.log(rank + " *** " + pic + " *** " + profile.name + " *** " + points);
								$('.board_container').append(
															               		"<div class='simple_leader'>" +
																		            "<div class='rank font-effect-shadow-multiple " +
																		            extraClass +
																		            " '>" +
																		            rank +
																		            "</div><div class='profile'><img src='" +
																		            pic +
																		            "'></div>" +
																		            "<div class='name' title='" +
																		            profile.name +
																		            "'>" +
																		            profile.name +
																		            "</div><div class='score'>" +
																		            points +
																		            "</div></div>"
																						);
						});
				}
    });
}