$(document).ready(function() {
	/*function outputProfile (profile) {
        console.log("got here");
        $('.profile_photo img').attr('src', profile.picture);
        $('.name_content').text(profile.name);
    }*/


	$.get("/api/leaderboard", function (data) {
		console.log("In jQuery GET callback:");
		var obj = JSON.parse(data);
		leaderboard = obj.data ;
		for (i = 0; i < leaderboard.length; i++) {
			id = leaderboard[i].id;
			points = leaderboard[i].points;

			//quizas_get_profile_for(id, outputProfile);
			console.log("called profile pic func");
		}
    })

});