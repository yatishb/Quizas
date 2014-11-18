$(document).ready(function() {


	$.get("/api/leaderboard", function (data) {
		console.log("In jQuery GET callback:");
		var obj = JSON.parse(data);
		leaderboard = obj.data ;
		for (i = 0; i < leaderboard.length; i++) {
			id = leaderboard[i].id.substring(9);
			points = leaderboard[i].points;
			pic = "http://graph.facebook.com/" + id + "/picture?type=square";

			console.log(pic);
		}
    })

});