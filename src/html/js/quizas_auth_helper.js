// Check which "sites" user already authorised with
// e.g. ["twitter"]
function quizas_authorized_sites() {
    var quizas_auth_sites = ["quizlet", "twitter"];
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
