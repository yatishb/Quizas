// Check which "sites" user already authorised with
// e.g. ["twitter"]
function quizas_authorized_sites() {
    var quizas_auth_sites = ["quizlet", "twitter", "facebook"];
    return quizas_auth_sites.filter(function (s) {
        return $.cookie(s + "_user_id") !== undefined;
    });
}

function quizas_logout() {
    var authSites = quizas_authorized_sites();

    authSites.forEach(function (s) {
        $.removeCookie(s + "_user_id", { path: "/" });
        $.removeCookie(s + "_access_token", { path: "/" });
    });
}

function quizas_is_authorized_for(site) {
    var sites = quizas_authorized_sites();
    return sites.indexOf(site) >= 0;
}

// Get a user id which we can pass to quizlet for #user-id fields
function quizas_user_id() {
    var authed_sites = quizas_authorized_sites();

    // Any will do, use the first one.
    // (And this will blow up if the user isn't authorized).
    var site = authed_sites[0];
    var user_id = site + ":" + $.cookie(site + "_user_id");
    return user_id; // e.g. `quizlet:rgoulter`
}


function quizas_update_auth_cookies(site, authId, authToken, redirectUrl) {
    // site e.g. "quizlet", "twitter", "facebook"

    // site is only for "facebook", btw.
    // if already logged in w/ a different Facebook acct.
    if (quizas_is_authorized_for("facebook") &&
        $.cookie("facebook_user_id") !== authId) {
        // CLASH! So, logout from current one.
        quizas_logout();
    }

    // Set the cookie
    $.cookie(site + "_user_id",
             authId,
             { expires: 365, path: '/' });
    $.cookie(site + "_access_token",
             authToken,
             { expires: 365, path: '/' });

    // Notify Quizas app about the new auth.
    // FIXME: This is a bit daft, isn't it? Fix for G+ integ.
    $.post("/api/facebookauthnotify", function (data) {
        // Redirect
        window.location.href = redirectUrl;
    });
}


// Explicitly, takes *userid*. e.g. 'quizlet:rgoulter'.
// n.b. currently, you can only get the Profile from the same
// site as the id is from.
// (i.e. if it's twitter, can't get facebook profile).
function quizas_get_profile_for(userid, profileCallback) {
    if(userid.indexOf("facebook:") >= 0) {
        // See quizas_facebook.js
        var fb_userid = userid;
        var fbid = fb_userid.substr("facebook:".length);

        return getFacebookProfile(fbid, profileCallback);
    } else if(userid.indexOf("twitter:") >= 0) {
        var twitter_userid = userid;
        var twid = twitter_userid.substr("twitter:".length);

        $.get("/api/profile/twitter/" + twid, function f(data) {
            profileCallback(JSON.parse(data));
        });
    } else if(userid.indexOf("quizlet:") >= 0) {
        var quizlet_userid = userid;
        var qzid = quizlet_userid.substr("quizlet:".length);

        $.get("/api/profile/quizlet/" + qzid, function f(data) {
            profileCallback(JSON.parse(data));
        });
    }
}


function quizas_get_profile(profileCallback) {
    if(quizas_is_authorized_for("facebook")) {
        // See quizas_facebook.js
        var fbid = $.cookie("facebook_user_id");
        return getFacebookProfile(fbid, profileCallback);
    } else if(quizas_is_authorized_for("twitter")) {
        var twid = $.cookie("twitter_user_id");
        $.get("/api/profile/twitter/" + twid, function f(data) {
            profileCallback(JSON.parse(data));
        });
    } else if(quizas_is_authorized_for("quizlet")) {
        var qzid = $.cookie("quizlet_user_id");
        $.get("/api/profile/quizlet/" + qzid, function f(data) {
            profileCallback(JSON.parse(data));
        });
    }
}

function outputFriendsStudy(friends) {
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
}