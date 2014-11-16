# Routes for user "challenges",
# which are a middleground between live multiplayer
# and single player.

import ast
import json
import requests

import authhelper
import secrets
import quizletsets
import internalstats

from flask import request, redirect, make_response
from models import UserChallenge, QuestionsChallenge
from . import main
from .. import db

STATUS_NEW            = "new"
STATUS_PENDING_RESULT = "pending_result" # Recipient still needs to play
STATUS_PENDING_SEEN   = "pending_seen"   # Challenger still needs to see result
STATUS_DONE           = "done"

# class UserChallenge(db.Model):
#  challengerId = db.Column(db.Integer)
#  recipientId  = db.Column(db.Integer)
#  gameId       = db.Column(db.String(40), primary_key = True)
#  status       = db.Column(db.String(80))

# POST /user/<useridA>/challenges/<useridB>/<setid>
# Posts a new challenge from user A vs user B, with the given set id.
@main.route('/user/<challengerId>/challenges/<recipientId>/<setid>', methods=['POST'])
def create_new_challenge(challengerId, recipientId, setid):
	current_id = authhelper.get_current_id()
	chgr_id = authhelper.lookup(challengerId)

	if current_id != chgr_id:
		return "Challenger must be logged in"

	rcpt_id = authhelper.lookup(recipientId)

	# Receive the post stats JSON. Post a new game in the DB.
	if request.json:
		receivedData = request.get_json()

		# Post the results, using `internalstats`
		# (since it's FlashGame, FlashCardInGame)
		gameId = internalstats.soloGameResultsWriteDb(chgr_id,
		                                              receivedData)

		# Add new row to QuestionsChallenge
		qc = QuestionsChallenge(gameId, json.dumps(receivedData['questions']))
		db.session.add(qc)

		# Add new row to UserChallenge
		uc = UserChallenge(chgr_id, rcpt_id, gameId, STATUS_NEW)
		db.session.add(uc)
		db.session.commit()

		return "Successfully updated"
	else:
		# Return invalid request?
		return "No post body given"



# GET /user/<useridA>/challenges/
# Gets list of all challenges; results of challenges.
# Returns JSON format ... ???
@main.route('/user/<challengerId>/challenges/')
def get_challenges(challengerId):
	chgr_id = authhelper.lookup(challengerId)
	# Make an API request getting all the challenges which have this guy
	# as a recipient, and are pending.
	to_play = UserChallenge.query.filter_by(recipientId = chgr_id,
	                                        status = STATUS_NEW).all()

	# AND those which him as a challenger, which still need to be "seen"
	to_see = UserChallenge.query.filter_by(challengerId = chgr_id,
	                                       status = STATUS_PENDING_SEEN).all()

	# For each, we need to return
	# {recipUserId, gameId, setId}
	# and score/result, also.

	def lookupSetForGameId(gameId):
		return FlashGame.query.filter_by(user = chgr_id,
		                                 gameId = gameId).first()

	to_play_dict = [{recipientUserId: authhelper.lookupInternal(challenge.recipientId),
	                 gameId: challenge.gameId,
	                 setId: lookupSetForGameId(challenge.gameId)}
	                for challenge in to_play]

	to_see_dict = [{recipientUserId: authhelper.lookupInternal(challenge.recipientId),
	                gameId: challenge.gameId,
	                setId: lookupSetForGameId(challenge.gameId)}
	               for challenge in to_play]

	# TODO: How get win/loss/draw?
	# (score for each?)
	# or just return the game ID; and let
	# clientside access other /stats endpoints?

	return json.dumps({"pending": to_play_dict,
	                   "done": to_see_dict})



# POST /user/<userid>/challenges/complete/<gameId>
# When the second user finishes a challenge, they can post to this to finish it.
@main.route('/user/<challengerId>/challenges/complete/<gameId>', methods=['POST'])
def finish_challenge(challengerId, gameId):
	current_id = authhelper.get_current_id()
	chgr_id = authhelper.lookup(challengerId)

	if current_id != chgr_id:
		return "Challenger must be logged in"

	result = UserChallenge.query.get(gameId)
	
	if result != None and request.json:
		receivedData = request.get_json()

		# Post the results, using `internalstats`
		# (since it's FlashGame, FlashCardInGame)
		gameId = internalstats.soloGameResultsWriteDbWithGameId(chgr_id,
		                                                        gameId,
		                                                        receivedData)

		# Now that the recipient of the challenge has logged in, update the
		# status of the challenge to "waiting for challenger to see the results"
		result.status = STATUS_PENDING_SEEN
		db.session.commit()

		return "Successfully updated"
	else:
		return "Invalid request"



# POST /user/<userid>/challenges/seen/<gameid>
# Acknowledge that the user has seen the result of a challenge.
@main.route('/user/<challengerId>/challenges/seen/<gameId>', methods=['POST'])
def seen_challenge_result(challengerId, gameId):
	current_id = authhelper.get_current_id()
	chgr_id = authhelper.lookup(challengerId)

	if current_id != chgr_id:
		return "Challenger must be logged in"

	# Get the challenge with the game ID,
	# and set the status to be "DONE"
	result = UserChallenge.query.get(gameId)
	
	if result != None:
		result.status = STATUS_DONE
		db.session.commit()

		return "Successfully updated"
	else:
		return "Invalid request"
