import requests
import ast

from flask import Blueprint
from flask import request, redirect
quizletauth = Blueprint('quizletauth', __name__)

@quizletauth.route("/quizletauth")
def auth1():
	clientID = "bgT4xYAXqK"
	redirectUrl = "http://54.169.123.39:5000/quizletauthstep2"
	randomStateString = "quiwas"
	# clientID = 'p8UvFSHYUd' # use for localhost testing
	redirectUrl = 'http://127.0.0.1:5000/quizletauthstep2' # use for localhost testing
	authorizeUrl = "https://quizlet.com/authorize?client_id=" +clientID + "&response_type=code&scope=read%20write_set"

	url = authorizeUrl + "&state=" + randomStateString +"&redirect_uri=" + redirectUrl
	return redirect(url)


@quizletauth.route("/quizletauthstep2")
def authparam():
	tokenUrl = "https://api.quizlet.com/oauth/token"
	randomStateString = "quiwas"
	clientID = "bgT4xYAXqK"
	keySecret = "62FgV2eBuE6EATxncscuek"
	# clientID = 'p8UvFSHYUd' # use for localhost testing
	# keySecret = 'fAzdhfBnTPkGvgBqPwbHTX' # use for localhost testing

	state = request.args.get('state')
	if state != randomStateString :
		return "Didn't receive correct state"

	code = request.args.get('code')
	grant_type = "authorization_code"
	redirect_uri = 'http://127.0.0.1:5000/quizletauthstep2'
	payload = {'code' : code, 'grant_type' : grant_type, 'redirect_uri' : redirect_uri}

	req = requests.post(tokenUrl, data=payload, auth=(clientID, keySecret))
	if req.status_code != 200 :
		return "Bad Request"
	else :
		receivedPayload = ast.literal_eval(req.text)
		accessToken = receivedPayload['access_token']
		userId = receivedPayload['user_id']
		return accessToken