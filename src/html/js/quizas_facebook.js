// We have different App IDs for quizas.me and localhost
var quizas_fbappid = (window.location.hostname === "quizas.me") ? 
                     "886033551408121" :
                     "886034451408031";

// Function to perform Graph API call to list FB friends.
// friendsCallback takes in one argument, which is
// an array of {name:, userid:} objects.
function listFacebookFriends(friendsCallback) {
  // Make sure user is logged in.
  FB.getLoginStatus(function(response) {
    if (response.status === 'connected') {
        FB.api(
            "/me/friends",
            function (response) {
                if (response && !response.error) {
                    // response.data = [{name, id}]
                    function toQuizazRep(f){
                        return {"name": f.name,
                                "userid": "facebook:" + f.id}
                    }

                    friendsCallback(response.data.map(toQuizazRep));
                }
            }
        );
    } else {
      //FB.login();
    }
  });
}

// n.b. fbid != Quizas' userid.
// We want {name, picture}
// This is given to profileCallback
function getFacebookProfile(fbid, profileCallback) {
  // Make sure user is logged in.
  FB.getLoginStatus(function(response) {
    if (response.status === 'connected') {
      // https://developers.facebook.com/docs/graph-api/reference/v2.2/user
      FB.api(
        "/" + fbid,
        function (response) {
          if (response && !response.error) {
            // Strictly, profile pic can be public.
            // https://developers.facebook.com/docs/graph-api/reference/v2.2/user/picture/
            FB.api(
              "/" + fbid + "/picture",
              {
                "redirect": false,
                "type": "normal"
              },
              function (picResponse) {
                if (picResponse && !picResponse.error) {
                  profileCallback({"name": response.name,
                                   "picture": picResponse.data.url});
                }
              }
            );
          }
        }
      );
    } else {
      //FB.login();
    }
  });
}
