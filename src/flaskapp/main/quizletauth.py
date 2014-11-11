import requests
import ast
import json

import authhelper
import secrets

from flask import request, redirect, make_response
from . import main

CONSUMER_TOKEN  = secrets.auth["quizlet"]["client_id"]
CONSUMER_SECRET = secrets.auth["quizlet"]["key_secret"]
CALLBACK_URL    = secrets.auth["quizlet"]["redirect_url"]

@main.route("/quizletauth")
def auth1():
	clientID = CONSUMER_TOKEN
	redirectUrl = CALLBACK_URL
	randomStateString = "quiwas"
	authorizeUrl = "https://quizlet.com/authorize?client_id=" + clientID + "&response_type=code&scope=read%20write_set"

	url = authorizeUrl + "&state=" + randomStateString + "&redirect_uri=" + redirectUrl
	return redirect(url)


@main.route("/quizletauthstep2")
def authparam():
	tokenUrl = "https://api.quizlet.com/oauth/token"
	randomStateString = "quiwas"
	clientID = CONSUMER_TOKEN
	keySecret = CONSUMER_SECRET

	state = request.args.get('state')
	if state != randomStateString :
		return "Didn't receive correct state"

	code = request.args.get('code')
	grant_type = "authorization_code"
	redirect_uri = CALLBACK_URL
	payload = {'code' : code, 'grant_type' : grant_type, 'redirect_uri' : redirect_uri}

	req = requests.post(tokenUrl, data=payload, auth=(clientID, keySecret))
	if req.status_code != 200 :
		return "Bad Request"
	else :
		receivedPayload = ast.literal_eval(req.text)
		accessToken = receivedPayload['access_token']
		userId = receivedPayload['user_id']
		jsonData = {}
		jsonData['id'] = userId
		jsonData['token'] = accessToken

		# Stretching the definition of "auth" a bit here, but..
		resp = redirect(secrets.auth["login_success_url"]); # make_response(json.dumps(jsonData))

		new_userid = "quizlet:" + userId
		if authhelper.userids_clash_userid(new_userid):
			# A different user was previously logged in on this
			# browser (i.e. different w/ different quizlet acct).
			# Delete their cookies.
			for site in authhelper.auth_sites:
				if request.cookies.get(site + "_user_id") != None:
					resp.set_cookie(site + "_user_id", '', expires = 0)

		resp.set_cookie("quizlet_user_id", userId, max_age = 3600*24*30)
		resp.set_cookie("quizlet_access_token", accessToken, max_age = 3600*24*30)

		# Ensure user has an internal user id we can use.
		authhelper.register(new_userid)

		return resp



# Get Quizlet username + profile picture url.
@main.route("/profile/quizlet/<qzlt_id>")
def get_quizlet_profile(qzlt_id):
	clientID = CONSUMER_TOKEN
	keySecret = CONSUMER_SECRET

	qzlt_user_url = "https://api.quizlet.com/2.0/users/" + qzlt_id

	# Get ACCESS TOKEN from Cookies
	qzlt_access_token = request.cookies.get("quizlet_access_token")
	if qzlt_access_token == None:
		# If no user access token, just use CLIENT ID to access public sets
		req = requests.get(qzlt_user_url, params = {"client_id": clientID})
	else:
		# FIXME: Not sure how to pass access token to `requests` properly
		req = requests.get(qzlt_user_url, headers = {"Authorization": "Bearer " + qzlt_access_token})

	if req.status_code != 200 :
		return {"error": "Bad Request: " + req.text}
	else :
		qzlt_json = json.loads(req.text)
		return json.dumps({"name": qzlt_json["username"],
		                   "picture": qzlt_json["profile_image"]})
