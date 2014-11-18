from . import main
import json
from flask import request, abort
import internalstats, authhelper

@main.route('/user/<userid>/stats', methods=['GET'])
def displayUserStats(userid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return internalstats.getIndividualUserGameStats(internalUserid)

@main.route('/user/<userid>/stats/vs/<opponent>', methods=['GET'])
def displayUserStatsHeadToHead(userid, opponent):
	internalUserid = authhelper.lookup(userid)
	opponentUserid = authhelper.lookup(opponent)
	if internalUserid == None or opponentUserid == None:
		abort(401)
	else:
		if internalUserid == opponentUserid:
			abort(401)
		else:
			return internalstats.getCommonGamesStats(internalUserid, opponentUserid)

@main.route('/user/<userid>/stats/games', methods=['GET'])
def displayUserGamesPlayed(userid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return internalstats.getUserGamesJSON(internalUserid)

@main.route('/user/<userid>/stats/game/<gameid>', methods=['GET'])
def displayUserGameStats(userid, gameid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return internalstats.getGameStats(internalUserid, gameid)

@main.route('/user/<userid>/stats/sets/<setid>', methods=['GET'])
def displayUserSetStats(userid, setid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return internalstats.getUserSetStats(internalUserid, setid)

@main.route('/user/<userid>/gameresults', methods=['POST'])
def readStatsOfJustEndedGame(userid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		if request.json:
			receivedData = request.get_json()
			internalstats.soloGameResultsWriteDb(internalUserId, receivedData)
			return "Successfully updated"
		else:
			abort(401)


@main.route('/leaderboard')
def buildLeaderboard():
	return json.dumps( {'data':internalstats.populateLeaderboard()} )
