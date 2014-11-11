// Check which "sites" user already authorised with
// e.g. ["twitter"]
function quizas_authorized_sites() {
    var quizas_auth_sites = ["quizlet", "twitter", "facebook"];
    return quizas_auth_sites.filter(function (s) {
        return $.cookie(s + "_user_id") !== undefined;
    });
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


function quizas_update_auth_cookies(site, authId, authToken) {
    // site e.g. "quizlet", "twitter", "facebook"

    // Check what other cookies Quizas has,
    // if they clash (has this site, but different authId), remove the others.
    if ($.cookie(site + "_user_id") != authId) {
        var auth_sites = ["quizlet", "twitter", "facebook"]; // BAD MAGIC
        for (var i in auth_sites) {
            var s = auth_sites[i];

            // No great harm in removing a cookie which isn't there.
            $.removeCookie(s + "_user_id", { path: "/" });
            $.removeCookie(s + "_access_token", { path: "/" });
        }
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
    $.post("/api/facebookauthnotify");
}
