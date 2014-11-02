# For all the Quizlet things.

import requests
import ast
import json

import secrets

from models import UserFlashSet
from flask import request, redirect, abort
from . import main
from .. import db

CONSUMER_TOKEN  = secrets.auth["quizlet"]["client_id"]
CONSUMER_SECRET = secrets.auth["quizlet"]["key_secret"]
CALLBACK_URL    = secrets.auth["quizlet"]["redirect_url"]

# /user/#user-id/sets
@main.route('/user/<user_id>/sets')
def get_user_sets(user_id):
	result = UserFlashSet.query.filter_by(user = user_id).all()
	set_ids = [user_flashset.flashsetId for user_flashset in result]
	return json.dumps(set_ids)

# /user/#user-id/sets/#set-id
@main.route('/user/<user_id>/sets/<set_id>', methods=['PUT', 'DELETE'])
def modify_user_sets(user_id, set_id):
	# ACTION = PUT, DELETE

	current = UserFlashSet.query \
	                      .filter_by(user = user_id, flashsetId = set_id) \
	                      .all()
	if request.method == 'PUT':
		if len(current) == 0:
			user_flashset = UserFlashSet(user_id, set_id)
			db.session.add(user_flashset)
	if request.method == 'DELETE':
		db.session.delete(current[0])

	db.session.commit()

	return json.dumps({"result": "ok"})



#
# Quizlet Wrapping API
#


# /sets/#set-id
# Expects set-id as `quizlet:SET_ID`
# Quizlet API, see:
# https://quizlet.com/api/2.0/docs/sets#view
@main.route('/sets/<set_id>')
def get_quizlet_set(set_id):
	if set_id[:8] == "quizlet:":
		qzlt_set_id = set_id[8:]

		tokenUrl = "https://api.quizlet.com/oauth/token"
		clientID = CONSUMER_TOKEN
		keySecret = CONSUMER_SECRET

		# Get ACCESS TOKEN from Cookies
		qzlt_access_token = request.cookies.get("quizlet_access_token")
		if qzlt_access_token == None:
			abort(401)

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



# For many Quizlet API endpoints,
# FlashSets are returned without a list of terms.
# For these, we represent this to Quizas app with
#   {id, name, description, size}
def termless_set_to_rep(qzlt_set):
	return {"id": "quizlet:" + str(qzlt_set["id"]),
	        "name": qzlt_set["title"],
	        "description": qzlt_set.get("description"),
	        "size": qzlt_set["term_count"]}




# /sets/search/#query
# See:
# https://quizlet.com/api/2.0/docs/searching-sets
@main.route('/sets/search/<query>')
def quizlet_search(query):
	tokenUrl = "https://api.quizlet.com/oauth/token"
	clientID = CONSUMER_TOKEN
	keySecret = CONSUMER_SECRET

	# Get ACCESS TOKEN from Cookies
	qzlt_access_token = request.cookies.get("quizlet_access_token")
	if qzlt_access_token == None:
		abort(401)

	# Params for the search
	payload = {'q': query}

	# FIXME: Not sure how to pass access token to `requests` properly
	qzlt_search_url = "https://api.quizlet.com/2.0/search/sets"
	req = requests.get(qzlt_search_url,
	                   params = payload,
	                   headers = {"Authorization": "Bearer " + qzlt_access_token})

	if req.status_code != 200 :
		return "Bad Request: " + req.text
	else :
		# Return ... as per spec?
		# Can't, since the Quizlet API point doesn't return terms.
		# Clientside can request indiv. set later.
		search_result = json.loads(req.text)

		# Map from .sets to some return value
		# Return [{id: "quizlet:SET_ID", name, size: TERM_COUNT}]
		return json.dumps([termless_set_to_rep(qzlt_set) for qzlt_set in search_result["sets"]])



# Helper method to access Quizlet User endpoint.
# Main limitation is "recently studied" returns most recent 25,
# not most recent hundred.
# Also, user-created and favourited *could* return all the terms
# if that endpoint is accessed directly
# See: https://quizlet.com/api/2.0/docs/users
def quizlet_user(user_id):
	tokenUrl = "https://api.quizlet.com/oauth/token"
	clientID = CONSUMER_TOKEN
	keySecret = CONSUMER_SECRET

	# Get ACCESS TOKEN from Cookies
	# Needs to have user id also.
	qzlt_user_id = request.cookies.get("quizlet_user_id")
	qzlt_access_token = request.cookies.get("quizlet_access_token")
	if qzlt_access_token == None or qzlt_user_id == None:
		abort(401)

	# FIXME: Not sure how to pass access token to `requests` properly
	# n.b. username is `qzlt_user_id`
	qzlt_user_url = "https://api.quizlet.com/2.0/users/" + qzlt_user_id
	req = requests.get(qzlt_user_url,
	                   headers = {"Authorization": "Bearer " + qzlt_access_token})

	if req.status_code != 200 :
		return "Bad Request: " + req.text
	else :
		return json.loads(req.text)

# /user/#user-id/sets/quizlet/created
# Quizlet API, see:
# https://quizlet.com/api/2.0/docs/users
@main.route('/user/<user_id>/sets/quizlet/created')
def quizlet_user_created(user_id):
	res = quizlet_user(user_id)
	sets = res["sets"]
	
	# Filter through so that set's visibility is "public"
	# (otherwise, may blow up trying to get set, since competing with
	#  a flashset surely requires both ppl to have access to it).
	public_sets = [termless_set_to_rep(ps) for ps in sets if ps["visibility"] == "public"]
	return json.dumps(public_sets)

# /user/#user-id/sets/quizlet/favorites
# Quizlet API, see:
# https://quizlet.com/api/2.0/docs/users
@main.route('/user/<user_id>/sets/quizlet/favorites')
def quizlet_user_favourites(user_id):
	res = quizlet_user(user_id)
	sets = res["favorite_sets"]
	
	# Filter through so that set's visibility is "public"
	# (otherwise, may blow up trying to get set, since competing with
	#  a flashset surely requires both ppl to have access to it).
	public_sets = [termless_set_to_rep(ps) for ps in sets if ps["visibility"] == "public"]
	return json.dumps(public_sets)

# /user/#user-id/sets/quizlet/studied
# Quizlet API, see:
# https://quizlet.com/api/2.0/docs/users
@main.route('/user/<user_id>/sets/quizlet/studied')
def quizlet_user_studied(user_id):
	res = quizlet_user(user_id)
	study_sessions = res["studied"]
	
	# Filter through so that set's visibility is "public"
	# (otherwise, may blow up trying to get set, since competing with
	#  a flashset surely requires both ppl to have access to it).
	public_sets = [termless_set_to_rep(ps["set"]) for ps in study_sessions if ps["set"]["visibility"] == "public"]
	return json.dumps(public_sets)




