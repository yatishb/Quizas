from . import main
from flask import request, abort
import accessdb, authhelper

@main.route('/user/<userid>/stats', methods=['GET'])
def displayUserStats(userid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return accessdb.getUserWinLossStats(internalUserid)

@main.route('/user/<userid>/stats/vs/<opponent>', methods=['GET'])
def displayUserStatsHeadToHead(userid, opponent):
	internalUserid = authhelper.lookup(userid)
	opponentUserid = authhelper.lookup(opponent)
	if internalUserid == None or opponentUserid == None:
		abort(401)
	else:
		return accessdb.getUserWinLossStats(internalUserid, opponentUserid)

@main.route('/user/<userid>/stats/games', methods=['GET'])
def displayUserGamesPlayed(userid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return accessdb.getUserGames(internalUserid)

@main.route('/user/<userid>/stats/game/<gameid>', methods=['GET'])
def displayUserGameStats(userid, gameid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return accessdb.getGameStats(internalUserId, gameid)

@main.route('/user/<userid>/stats/sets/<setid>', methods=['GET'])
def displayUserSetStats(userid, setid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		return accessdb.getUserSetStats(internalUserid, setid)

@main.route('/user/<userid>/gameresults', methods=['POST'])
def readStatsOfJustEndedGame(userid):
	internalUserid = authhelper.lookup(userid)
	if internalUserid == None:
		abort(401)
	else:
		if request.json:
			receivedData = request.get_json()
			accessdb.soloGameResultsWriteDb(internalUserId, receivedData)
			return "Successfully updated"
		else:
			abort(401)
