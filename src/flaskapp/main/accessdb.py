from models import User, FlashGame as FG, FlashCardInGame as FC
from sqlalchemy import func
from . import main
from .. import db, redis
import json, uuid


# Parameters: room, user1, user2, redis.hgetall(HASH_USER1), redis.hgetall(HASH_USER2), flashsetid
# user1 and user2 are integers
# redis.hgetall(HASH_USER1) gives dict of FlashcardID and UserAnswer
# The equivalent parameter for that is userAns1
def documentGame(room, user1, user2, userAns1, userAns2, flashsetId) :
	# Store game header in FlashGame db
	gameUser1 = FG(room, flashsetId, user1)
	gameUser2 = FG(room, flashsetId, user2)
	db.session.add(gameUser1)
	db.session.add(gameUser2)

	allQuestions = userAns1.keys()

	for questionId in allQuestions:
		user1AnsChosen = userAns1.get(questionId)
		user2AnsChosen = userAns2.get(questionId)

		cardUser1 = FC(room, flashsetId, questionId, user1, user1AnsChosen)
		cardUser2 = FC(room, flashsetId, questionId, user2, user2AnsChosen)
		db.session.add(cardUser1)
		db.session.add(cardUser2)

	db.session.commit()


def soloGameResultsWriteDb(userid, receivedData) :
	flashsetId = receivedData['flashset']
	cards = receivedData['cards']
	gameId = str(uuid.uuid1())

	gameUser = FG(gameId, flashsetId, userid)
	db.session.add(gameUser)

	for eachQues in cards:
		questionId = eachQues['flashcard']
		userAns = eachQues['result']
		userIsCorrect = True # Must check whether ans is correct
		cardUser = FC(gameId, flashsetId, questionId, userid, userAns, userIsCorrect)
		db.session.add(cardUser)

	db.session.commit()


def getUserWinLossStats(userid, opponentUserId = None):
	# Find all games where one user is userid
	# Retrieve all cards for each game and individually compute if userid won
	if opponentUserId == None:
		gamesRetrieved = getUserGames(userid)
	else:
		gamesRetrieved = getCommonGames(userid, opponentUserId)

	allGamesUserPlayed = json.loads(gamesRetrieved)
	if len(allGamesUserPlayed) == 0:
		return "Haven't played"


	noOfWins = 0
	noOfLosses = 0
	noOfDraws = 0
	for eachGameId in allGamesUserPlayed:
		allQuestionsInGame = FC.query.filter(FC.gameId == eachGameId).all()
		
		noOfQuestionsCorrectUser = 0
		noOfQuestionsCorrectOpponent = 0
		for row in allQuestionsInGame:
			if row.user == userid:
				if row.isCorrect == True:
					noOfQuestionsCorrectUser += 1
			else:
				if row.isCorrect == True:
					noOfQuestionsCorrectOpponent += 1

		if noOfQuestionsCorrectUser > noOfQuestionsCorrectOpponent:
			noOfWins += 1
		elif noOfQuestionsCorrectUser < noOfQuestionsCorrectOpponent:
			noOfLosses += 1
		else:
			noOfDraws += 1

	numPlayed = noOfDraws + noOfWins + noOfLosses
	return json.dumps({'#Played': numPlayed, 
				'#Wins': noOfWins, 
				'#Losses': noOfLosses, 
				'#Draws': noOfDraws})


# Return list of gameids of the games played by the user
def getUserGames(userid):
	allGamesUserPlayed = FG.query.with_entities(FG.gameId).\
							group_by(FG.gameId).\
							having(FG.user == userid).\
							having(func.count() == 2)
	gameIds = []
	for eachGamePlayedByUser in allGamesUserPlayed:
		gameIds.append(eachGamePlayedByUser.gameId)
	return json.dumps(gameIds)


# Return list of common gameids of the games played by both
def getCommonGames(userid, opponentUserId):
	userGames = FG.query.filter(FG.user == userid).\
					with_entities(FG.gameId)
	oppoGames = FG.query.filter(FG.user == opponentUserId).\
					with_entities(FG.gameId)
	commonGames = []

	gameIds = []
	for eachGamePlayedByUser in userGames:
		gameIds.append(eachGamePlayedByUser.gameId)

	userGamesSet = set(gameIds)

	for eachGameOppo in oppoGames:
		gameid = eachGameOppo.gameId
		if gameid in userGamesSet:
			commonGames.append(gameid)

	return json.dumps(commonGames)



# Returns stats of a particular game
# These stats are such provided such that the 
# results page can be replicated without any problem
def getGameStats(userid, gameidForStats):
	questionsInGame = FC.query.filter(FC.gameId == gameidForStats).all()
	opponentUserId = ""
	gameResult = ""

	noOfQuestions = 0
	noOfQuestionsCorrectUser = 0
	noOfQuestionsCorrectOpponent = 0
	
	for row in questionsInGame:
		if row.user == userid:
			noOfQuestions += 1
			if row.isCorrect == True:
				noOfQuestionsCorrectUser += 1
		else:
			opponentUserId = row.user
			if row.isCorrect == True:
				noOfQuestionsCorrectOpponent += 1

	if noOfQuestionsCorrectUser > noOfQuestionsCorrectOpponent:
		gameResult = "Won"
	elif noOfQuestionsCorrectUser < noOfQuestionsCorrectOpponent:
		gameResult = "Lost"
	else:
		gameResult = "Drew"

	return json.dumps({"#Questions":noOfQuestions, 
				"#Correct":noOfQuestionsCorrectUser, 
				"AgainstUser":opponentUserId, 
				"#AgainstCorrect":noOfQuestionsCorrectOpponent, 
				"Result":gameResult})



# Returns stats of a particular user in a particular flashset
# Get all multiplayer games played
# Search amongst these multiplayer games if the user has played using the flashset
def getUserSetStats(userid, setid):
	allGamesUserPlayed = FG.query.with_entities(FG.gameId).\
							group_by(FG.gameId).\
							having(FG.user == userid).\
							having(FG.flashsetId == setid).\
							having(func.count() == 2)
	noOfWins = 0
	noOfLosses = 0
	noOfDraws = 0

	for eachGamePlayed in allGamesUserPlayed:
		eachGameId = eachGamePlayed.gameId
		allQuestionsInGame = FC.query.filter(FC.gameId == eachGameId).all()
		
		noOfQuestionsCorrectUser = 0
		noOfQuestionsCorrectOpponent = 0
		for row in allQuestionsInGame:
			if row.user == userid:
				if row.isCorrect == True:
					noOfQuestionsCorrectUser += 1
			else:
				if row.isCorrect == True:
					noOfQuestionsCorrectOpponent += 1

		if noOfQuestionsCorrectUser > noOfQuestionsCorrectOpponent:
			noOfWins += 1
		elif noOfQuestionsCorrectUser < noOfQuestionsCorrectOpponent:
			noOfLosses += 1
		else:
			noOfDraws += 1

	numPlayed = noOfDraws + noOfWins + noOfLosses
	return json.dumps({'#Played': numPlayed, 
				'#Wins': noOfWins, 
				'#Losses': noOfLosses, 
				'#Draws': noOfDraws})