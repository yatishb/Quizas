import requests
import ast
import json

import authhelper
import secrets

from flask import request, redirect, make_response
from . import main

# Since we do Facebook auth clientside, we have this route
# so that the client can notify the server when the user has logged in.
# Consistent with the same shit-arse approach, use cookies to communicate this.
#   $.post("/api/facebookauthnotify");
@main.route("/facebookauthnotify", methods = ['POST'])
def facebook_notify_auth():
	new_userid = "facebook:" + request.cookies.get("facebook_user_id")

	resp = make_response(json.dumps({"status": "ok"}));

	if authhelper.userids_clash_userid(new_userid):
		# A different user was previously logged in on this
		# browser (i.e. different w/ different quizlet acct).
		# Delete their cookies.
		for site in authhelper.auth_sites:
			if request.cookies.get(site + "_user_id") != None:
				resp.set_cookie(site + "_user_id", '', expires = 0)
	
	authhelper.register(new_userid)

	return resp
