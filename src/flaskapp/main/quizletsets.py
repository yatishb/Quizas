# For all the Quizlet things.

import requests
import ast
import json

import secrets

from flask import request, redirect
from . import main

CONSUMER_TOKEN  = secrets.quizlet_client_id
CONSUMER_SECRET = secrets.quizlet_key_secret
CALLBACK_URL    = secrets.quizlet_redirect_url

# /sets/#set-id
# Expects set-id as `quizlet:SET_ID`
# Quizlet API, see:
# https://quizlet.com/api/2.0/docs/sets#view
@main.route('/sets/<set_id>')
def show_user_profile(set_id):
	if set_id[:8] == "quizlet:":
		qzlt_set_id = set_id[8:]

		tokenUrl = "https://api.quizlet.com/oauth/token"
		clientID = CONSUMER_TOKEN
		keySecret = CONSUMER_SECRET

		# Get ACCESS TOKEN from Cookies
		qzlt_access_token = request.cookies.get("quizlet_access_token")

		payload = {}

		# FIXME: Not sure how to pass access token to `requests` properly
		qzlt_set_url = "https://api.quizlet.com/2.0/sets/" + qzlt_set_id
		req = requests.get(qzlt_set_url, headers={"Authorization": "Bearer " + qzlt_access_token})

		if req.status_code != 200 :
			return "Bad Request: " + req.text
		else :
			# Map from
			# qzlt.id -> "quizlet:" + id
			# qzlt.title -> name
			# ??? -> category
			# [{id, term, definition}] -> [{id, question, answer}]

			qzlt_json = json.loads(req.text)
			app_json = {"id": "quizlet:" + str(qzlt_json["id"]),
					    "name": qzlt_json["title"],
						"category": "???",
						"cards": [{"id": "quizlet:" + str(term["id"]),
						           "question": term["term"],
								   "answer": term["definition"]} for term in qzlt_json["terms"]]}
			return json.dumps(app_json)
	else:
		return "Invalid format"



# /user/#user-id/sets

# /user/#user-id/sets/#set-id

# /sets/search/#query


