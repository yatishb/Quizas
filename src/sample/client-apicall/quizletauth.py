import requests
import ast

import secrets

from flask import Blueprint
from flask import request, redirect, session
from flask import make_response
quizletauth = Blueprint('quizletauth', __name__)

@quizletauth.route("/quizletauth")
def auth1():
	clientID = secrets.quizlet_client_id
	redirectUrl = secrets.quizlet_redirect_url
	randomStateString = "quiwas"
	authorizeUrl = "https://quizlet.com/authorize?client_id=" + clientID + "&response_type=code&scope=read%20write_set"

	url = authorizeUrl + "&state=" + randomStateString + "&redirect_uri=" + redirectUrl
	return redirect(url)


@quizletauth.route("/quizletauthstep2")
def authparam():
	tokenUrl = "https://api.quizlet.com/oauth/token"
	randomStateString = "quiwas"
	clientID = secrets.quizlet_client_id
	keySecret = secrets.quizlet_key_secret

	state = request.args.get('state')
	if state != randomStateString :
		return "Didn't receive correct state"

	code = request.args.get('code')
	grant_type = "authorization_code"
	redirect_uri = secrets.quizlet_redirect_url
	payload = {'code' : code, 'grant_type' : grant_type, 'redirect_uri' : redirect_uri}

	req = requests.post(tokenUrl, data=payload, auth=(clientID, keySecret))
	if req.status_code != 200 :
		return "Bad Request"
	else :
		receivedPayload = ast.literal_eval(req.text)
		accessToken = receivedPayload['access_token']
		userId = receivedPayload['user_id']
		expires_in = receivedPayload['expires_in']
		# return accessToken

		fooo = request.cookies.get('foo')

		resp = redirect("http://dev.localhost/done.html")
		# resp.set_cookie("foo", "baz123", max_age=3600000*24)
		resp.set_cookie("notfoo", fooo);
		resp.set_cookie("quizas_user_id", userId);
		resp.set_cookie("quizas_access_token", accessToken);
		resp.set_cookie("quizas_expires_in", str(expires_in));
		return resp
