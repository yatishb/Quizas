import requests
import ast
import json

import authhelper
import secrets
import quizletsets

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

	authhelper.register(new_userid)
	quizletsets.ensure_some_flashsets(new_userid)

	return resp
