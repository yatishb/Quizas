from . import main
from flask import request
import accessdb

@main.route('/user/<userid>/stats', methods=['GET'])
def displayUserStats(userid):
	return accessdb.getUserWinLossStats(userid)

@main.route('/user/<userid>/stats/vs/<opponent>', methods=['GET'])
def displayUserStatsHeadToHead(userid, opponent):
	return accessdb.getUserWinLossStats(userid, opponent)

@main.route('/user/<userid>/stats/games', methods=['GET'])
def displayUserGamesPlayed(userid):
	return accessdb.getUserGames(userid)

@main.route('/user/<userid>/stats/game/<gameid>', methods=['GET'])
def displayUserGameStats(userid, gameid):
	return accessdb.getGameStats(userid, gameid)

@main.route('/user/<userid>/stats/sets/<setid>', methods=['GET'])
def displayUserSetStats(userid, setid):
	return accessdb.getUserSetStats(userid, setid)

@main.route('/user/<userid>/gameresults', methods=['POST'])
def readStatsOfJustEndedGame(userid):
	if request.json:
		receivedData = request.get_json()
		accessdb.soloGameResultsWriteDb(userid, receivedData)
		return "Successfully updated"
	else:
		return "Did not receive json"