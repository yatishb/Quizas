from models import User, FlashGame as FG, FlashCardInGame as FC
from sqlalchemy import func
from . import main
from .. import db
import json, uuid


def documentGame(room, roomClientAnswers, flashsetId) :
	allQuestions = roomClientAnswers.items()
	userNames = allQuestions[0][1].keys()
	user1 = userNames[0]
	user2 = userNames[1]
	gameUser1 = FG(room, flashsetId, user1)
	gameUser2 = FG(room, flashsetId, user2)
	db.session.add(gameUser1)
	db.session.add(gameUser2)

	for eachQues in allQuestions:
		questionId = eachQues[0]
		bothClientResp = eachQues[1]
		user1Ans = bothClientResp[user1]
		user2Ans = bothClientResp[user2]
		user1IsCorrect = True # Must check whether ans is correct
		user2IsCorrect = True # Must check whether ans is correct

		cardUser1 = FC(room, flashsetId, questionId, user1, user1Ans, user1IsCorrect)
		cardUser2 = FC(room, flashsetId, questionId, user2, user2Ans, user2IsCorrect)
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


def getUserGames(userid):
	# Return list of gameids of the games played by the user
	allGamesUserPlayed = FG.query.with_entities(FG.gameId).\
							group_by(FG.gameId).\
							having(FG.user == userid).\
							having(func.count() == 2)
	gameIds = []
	for eachGamePlayedByUser in allGamesUserPlayed:
		gameIds.append(eachGamePlayedByUser.gameId)
	return json.dumps(gameIds)

def getCommonGames(userid, opponentUserId):
	# Return list of common gameids of the games played by both
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



def getGameStats(userid, gameidForStats):
	# Returns stats of a particular game
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



def getUserSetStats(userid, setid):
	# Returns stats of a particular user in a particular flashset
	# Get all multiplayer games played
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