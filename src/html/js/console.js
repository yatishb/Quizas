$(document).ready(function() {
		setInterval( function() {
				$.get("/api/leaderboard", function (data) {
						var obj = JSON.parse(data);
						leaderboard = obj.data;
						console.log(obj);
					
						var element = $('.board_container');
						for (i = 0; i < leaderboard.length; i++) {
								id = leaderboard[i].id.substring(9);
								points = leaderboard[i].points;
								pic = "http://graph.facebook.com/" + id + "/picture?type=square";

								var extraClass = " ";
								if(i == 1) extraClass = "first";
								else if(i == 2) extraClass = "second";
								else if(i == 3) extraClass = "third";

								element.append(
								               		"<div class='simple_leader'>" +
								               		id +
											            "<div class='rank font-effect-shadow-multiple " +
											            extraClass +
											            " '>" +
											            name +
											            "</div><div class='profile'><img src='" +
											            pic +
											            "'></div>" +
											            "<div class='name' title='" +
											            name +
											            "'>" +
											            name +
											            "</div><div class='score'>" +
											            points +
											            "</div></div>"
															);
						}
		    });
		},
		18000);
});