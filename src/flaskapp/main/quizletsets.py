# For all the Quizlet things.

import requests
import ast
import json
import random

import secrets
import authhelper

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
	# NOTE: ignores user_id for now
	internal_id = authhelper.get_current_id()
	result = UserFlashSet.query.filter_by(user = internal_id).all()
	set_ids = [user_flashset.flashsetId for user_flashset in result]
	return json.dumps(set_ids)

# /user/#user-id/sets/#set-id
@main.route('/user/<user_id>/sets/<set_id>', methods=['PUT', 'DELETE'])
def modify_user_sets(user_id, set_id):
	# ACTION = PUT, DELETE

	# NOTE: ignores user_id for now
	internal_id = authhelper.get_current_id()

	current = UserFlashSet.query \
	                      .filter_by(user = internal_id, flashsetId = set_id) \
	                      .all()
	if request.method == 'PUT':
		if len(current) == 0:
			user_flashset = UserFlashSet(internal_id, set_id)
			db.session.add(user_flashset)
	if request.method == 'DELETE':
		db.session.delete(current[0])

	db.session.commit()

	return json.dumps({"result": "ok"})



#
# Quizlet Wrapping API
#

# Returns as dict, in raw Quizlet format
def get_raw_quizlet_set_json(qzlt_set_id):
	tokenUrl = "https://api.quizlet.com/oauth/token"
	clientID = CONSUMER_TOKEN
	keySecret = CONSUMER_SECRET

	qzlt_set_url = "https://api.quizlet.com/2.0/sets/" + qzlt_set_id

	# Get ACCESS TOKEN from Cookies
	qzlt_access_token = request.cookies.get("quizlet_access_token")
	if qzlt_access_token == None:
		# If no user access token, just use CLIENT ID to access public sets
		req = requests.get(qzlt_set_url, params = {"client_id": clientID})
	else:
		# FIXME: Not sure how to pass access token to `requests` properly
		req = requests.get(qzlt_set_url, headers = {"Authorization": "Bearer " + qzlt_access_token})

	if req.status_code != 200 :
		return {"error": "Bad Request: " + req.text}
	else :
		qzlt_json = json.loads(req.text)
		return qzlt_json



# Returns as dict, in Quizas format
def get_flashset_json(set_id):
	if set_id[:8] == "quizlet:":
		qzlt_set_id = set_id[8:]

		qzlt_json = get_raw_quizlet_set_json(qzlt_set_id)

		if "error" in qzlt_json:
			return qzlt_json
		else:
			# Map from
			# qzlt.id -> "quizlet:" + id
			# qzlt.title -> name
			# ??? -> category
			# [{id, term, definition}] -> [{id, question, answer}]

			app_json = {"id": "quizlet:" + str(qzlt_json["id"]),
					    "name": qzlt_json["title"],
						"category": "???",
						"cards": [{"id": "quizlet:" + str(term["id"]),
						           "question": term["term"],
								   "answer": term["definition"]} for term in qzlt_json["terms"]]}
			return app_json
	else:
		return {"error": "Invalid set_id format: " + set_id}

# /sets/#set-id
# Expects set-id as `quizlet:SET_ID`
# Quizlet API, see:
# https://quizlet.com/api/2.0/docs/sets#view
@main.route('/sets/<set_id>')
def get_flashset(set_id):
	set_json = get_flashset_json(set_id)

	if "error" in set_json:
		# FIXME: Could be more sophisticated about error codes & json, here
		return set_json["error"]
	else:
		return json.dumps(set_json)


def get_flashset_name(set_id):
	set_json = get_flashset_json(set_id)

	if "error" in set_json:
		return set_json
	else:
		set_name = set_json['title']
		return set_name



# Shuffled Quizset.
def shuffled_flashset_json(set_id, n):
	# Get the Flashset with the given id
	# in full Quizas set format
	set_json = get_flashset_json(set_id)

	if "error" in set_json:
		return set_json

	result = []
	shuffled_flashcards = []

	# Generate Questions:
	for i in xrange(0, n):
		# Draw cards.
		# If n <= len(set), great. Don't repeat
		# If n > len(set), need to repeat.
		if len(shuffled_flashcards) == 0:
			shuffled_flashcards = set_json["cards"][:] # Copy cards
			random.shuffle(shuffled_flashcards)

		# Since list is shuffled, just pop off last item,
		qn_card = shuffled_flashcards.pop()

		# Draw 3x OTHER cards. (4 answers per qn)
		# If I knew a better way. :/
		cards_not_qn = [c for c in set_json["cards"] if c != qn_card]
		random.shuffle(cards_not_qn)
		other_cards = cards_not_qn[0:3] # again, shuffled, so this is rndm

		answers = [qn_card] + other_cards
		random.shuffle(answers)

		# Shuffle the order of the cards; call  this a "Question"
		# {question: FCard, answers: [FCard]}
		# This is *somewhat* wasteful; quite wasteful if n > len.
		result.append({"question": qn_card,
		               "answers": answers})

	return {"questions": result}

@main.route('/sets/<set_id>/shuffle/<int:n>')
def shuffled_flashset(set_id, n):
	shuffled_json = shuffled_flashset_json(set_id, n)

	if "error" in shuffled_json:
		#FIXME: Be more sophisticated about error codes & JSON
		return shuffled_json["error"]

	return json.dumps(shuffled_json)



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

	# Params for the search
	qzlt_search_url = "https://api.quizlet.com/2.0/search/sets"

	# Get ACCESS TOKEN from Cookies
	qzlt_access_token = request.cookies.get("quizlet_access_token")
	if qzlt_access_token == None:
		# If no user access token, just use CLIENT ID to access public sets
		req = requests.get(qzlt_search_url,
		                   params = {"q": query, "client_id": clientID})
	else:
		# FIXME: Not sure how to pass access token to `requests` properly
		req = requests.get(qzlt_search_url,
		                   params = {"q": query},
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
	# NOTE: ignores user_id
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
	# NOTE: ignores user_id (in quizlet_user)
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
	# NOTE: ignores user_id (in quizlet_user)
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



# Initial quizsets
initial_flashsets = [# http://quizlet.com/2429383/basic-physics-final-review-flash-cards/
                     "quizlet:2429383",
                     # http://quizlet.com/57054880/french-human-body-first-1000-words-flash-cards/
                     "quizlet:57054880",
                     # http://quizlet.com/30160654/first-1000-words-in-spanish-la-granja-flash-cards/
                     "quizlet:30160654",
                     # http://quizlet.com/27972497/challenge-a-geography-terms-flash-cards/
                     # ^^ some of these are quite long; a test for the UI
                     "quizlet:27972497",
                     # http://quizlet.com/6860191/chemical-elements-flash-cards/
                     "quizlet:6860191",
                     # http://quizlet.com/249254/basic-japanese-vocabulary-romanji-flash-cards/
                     "quizlet:249254",
                     # http://quizlet.com/39050337/countries-and-capitals-flash-cards/
                     "quizlet:39050337",
                     # http://quizlet.com/51808929/currencies-flash-cards/
                     "quizlet:51808929",
                     # http://quizlet.com/56371322/best-picture-oscar-winners-by-year-and-lead-actors-flash-cards/,
                     "quizlet:56371322",
                     # http://quizlet.com/45551558/oscar-best-picture-winners-by-director-flash-cards/(HARD)
                     "quizlet:45551558"]


# Possibly repeated code w/ `modify_user_sets`.
def add_user_set(internal_id, set_id):
	current = UserFlashSet.query \
	                      .filter_by(user = internal_id, flashsetId = set_id) \
	                      .all()
	if len(current) == 0:
		user_flashset = UserFlashSet(internal_id, set_id)
		db.session.add(user_flashset)

	db.session.commit()


# This will ensure the user has them; no matter what.
def assign_initial_flashsets(internal_id):
	for set_id in initial_flashsets:
		add_user_set(internal_id, set_id)


# If the user has no flashsets; add some.
def ensure_some_flashsets(userid):
	internal_id = authhelper.lookup(userid)

	current = UserFlashSet.query \
	                      .filter_by(user = internal_id) \
	                      .all()
	
	if len(current) == 0:
		assign_initial_flashsets(internal_id)

		# If not a Quizlet userid, return
		if authhelper.site_of(userid) != "quizlet":
			return

		# For better integration with quizlet,
		# we could get the user, and add their
		quizlet_user_info = quizlet_user(userid)
		
		created_set_ids   = ["quizlet:" + str(s["id"]) for s in quizlet_user_info["sets"]]
		favorited_set_ids = ["quizlet:" + str(s["id"]) for s in quizlet_user_info["favorite_sets"]]
		studied_set_ids   = ["quizlet:" + str(s["set"]["id"]) for s in quizlet_user_info["studied"]]

		for set_id in created_set_ids + favorited_set_ids + studied_set_ids:
			# Ughh, this makes many more DB transactions than necessary
			add_user_set(internal_id, set_id)




# Favorite Sets

@main.route('/user/<user_id>/sets/quizlet/favorites/<set_id>', methods=['PUT', 'DELETE'])
def modify_quizlet_favorite_sets(user_id, set_id):
	tokenUrl = "https://api.quizlet.com/oauth/token"
	clientID = CONSUMER_TOKEN
	keySecret = CONSUMER_SECRET

	# "quizlet:1234" -> "1234"
	qzlt_set_id = set_id[set_id.find(':')+1:]

	# Get ACCESS TOKEN from Cookies
	# Needs to have user id also.
	# NOTE: ignores user_id
	qzlt_user_id = request.cookies.get("quizlet_user_id")
	qzlt_access_token = request.cookies.get("quizlet_access_token")
	if qzlt_access_token == None or qzlt_user_id == None:
		abort(401)

	# FIXME: Not sure how to pass access token to `requests` properly
	# n.b. username is `qzlt_user_id`
	qzlt_favorites_url = "https://api.quizlet.com/2.0/users/" + user_id + "/favorites/" + qzlt_set_id
	if request.method == 'PUT':
		req = requests.put(qzlt_favorites_url,
		                   headers = {"Authorization": "Bearer " + qzlt_access_token})
	else:
		req = requests.delete(qzlt_favorites_url,
		                      headers = {"Authorization": "Bearer " + qzlt_access_token})

	if req.status_code != 200 :
		return "Bad Request: " + req.text
	else :
		return json.loads(req.text)
