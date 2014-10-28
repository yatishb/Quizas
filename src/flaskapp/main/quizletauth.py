import requests
import ast
import json

import secrets

from flask import request, redirect, make_response
from . import main

CONSUMER_TOKEN  = secrets.quizlet_client_id
CONSUMER_SECRET = secrets.quizlet_key_secret
CALLBACK_URL    = secrets.quizlet_redirect_url

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

		resp = make_response(json.dumps(jsonData))

		resp.set_cookie("quizlet_user_id", userId)
		resp.set_cookie("quizlet_access_token", accessToken)

		return resp
