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

		# -1 refers to time taken by client for each answer
		cardUser1 = FC(room, flashsetId, questionId, user1, user1AnsChosen, -1)
		cardUser2 = FC(room, flashsetId, questionId, user2, user2AnsChosen, -1)
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
		cardUser = FC(gameId, flashsetId, questionId, userid, userAns, -1)
		db.session.add(cardUser)

	db.session.commit()



# def getUserWinLossStats(userid, opponentUserId = None):
# 	# Find all games where one user is userid
# 	# Retrieve all cards for each game and individually compute if userid won
# 	if opponentUserId == None:
# 		gamesRetrieved = getUserGames(userid)
# 	else:
# 		gamesRetrieved = getCommonGames(userid, opponentUserId)

# 	allGamesUserPlayed = json.loads(gamesRetrieved)
# 	if len(allGamesUserPlayed) == 0:
# 		return "Haven't played"


# 	noOfWins = 0
# 	noOfLosses = 0
# 	noOfDraws = 0
# 	for eachGameId in allGamesUserPlayed:
# 		allQuestionsInGame = FC.query.filter(FC.gameId == eachGameId).all()
		
# 		noOfQuestionsCorrectUser = 0
# 		noOfQuestionsCorrectOpponent = 0
# 		for row in allQuestionsInGame:
# 			if row.user == userid:
# 				if row.flashcardId == row.userAns:
# 					# Check if ans is correct
# 					noOfQuestionsCorrectUser += 1
# 			else:
# 				if row.flashcardId == row.userAns:
# 					# Check if ans is correct
# 					noOfQuestionsCorrectOpponent += 1

# 		if noOfQuestionsCorrectUser > noOfQuestionsCorrectOpponent:
# 			noOfWins += 1
# 		elif noOfQuestionsCorrectUser < noOfQuestionsCorrectOpponent:
# 			noOfLosses += 1
# 		else:
# 			noOfDraws += 1

# 	numPlayed = noOfDraws + noOfWins + noOfLosses
# 	return json.dumps({'#Played': numPlayed, 
# 				'#Wins': noOfWins, 
# 				'#Losses': noOfLosses, 
# 				'#Draws': noOfDraws})



# Given num of questions got correct by user and opponent, update win/draw/loss
def updateWinDrawLossStat(noOfQuestionsCorrectUser, noOfQuestionsCorrectOpponent, 
		noOfWins, noOfDraws, noOfLosses):
	if noOfQuestionsCorrectUser > noOfQuestionsCorrectOpponent:
		noOfWins += 1
	elif noOfQuestionsCorrectUser < noOfQuestionsCorrectOpponent:
		noOfLosses += 1
	else:
		noOfDraws += 1

	return noOfWins, noOfDraws, noOfLosses


def findNumOfQuesEachUserInGameGotCorrect(allQuestionsInGame, userid):
	noOfQuestionsCorrectUser = 0
	noOfQuestionsCorrectOpponent = 0

	for row in allQuestionsInGame:
		if row.user == userid:
			if row.flashcardId == row.userAns:
				# Check if ans is correct
				noOfQuestionsCorrectUser += 1
		else:
			if row.flashcardId == row.userAns:
				# Check if ans is correct
				noOfQuestionsCorrectOpponent += 1

	return noOfQuestionsCorrectUser, noOfQuestionsCorrectOpponent


# Return list of games played by the user as a JSON
def getUserGamesJSON(userid):
	return json.dumps(getUserGames(userid))

# Return list of games played by the user
def getUserGames(userid):
	userGames = FG.query.filter(FG.user == userid).\
					with_entities(FG.gameId)
	gameIds = []
	for eachGamePlayedByUser in userGames:
		gameIds.append(eachGamePlayedByUser.gameId)

	return gameIds




# Find list of gameids of the games played by the user
# Supposed to return only multiplayer games played
def getIndividualUserGameStats(userid):
	allGamesUserPlayed = getUserGames(userid)
	
	noOfWins = noOfLosses = noOfDraws = 0
	for eachGameId in allGamesUserPlayed:
		# Retrieve the gameids of each of the rows in the query
		# eachGameId = eachGamePlayedByUser.gameId
		
		# Retrieve complete details about the game
		allQuestionsInGame = FC.query.filter(FC.gameId == eachGameId).all()

		# Flag variable to detect if single player game
		singleGame = True
		for row in allQuestionsInGame:
			if row.user != userid:
				singleGame = False
		# If the game was found to be a single player, ignore game
		if singleGame == True:
			continue
				
		noOfQuestionsCorrectUser, noOfQuestionsCorrectOpponent = findNumOfQuesEachUserInGameGotCorrect(
																		allQuestionsInGame, userid)
		noOfWins, noOfDraws, noOfLosses = updateWinDrawLossStat(noOfQuestionsCorrectUser, 
									noOfQuestionsCorrectOpponent, noOfWins, noOfDraws, noOfLosses)

	numPlayed = noOfDraws + noOfWins + noOfLosses
	return json.dumps({'#Played': numPlayed, 
				'#Wins': noOfWins, 
				'#Losses': noOfLosses, 
				'#Draws': noOfDraws})
	


# Find list of common gameids of the games played by both
# Return stats on the multiplayer games played
def getCommonGamesStats(userid, opponentUserId):
	userGames = getUserGames(userid)
	oppoGames = getUserGames(opponentUserId)
	commonGames = []
	gameIds = []
	for eachGamePlayedByUser in userGames:
		gameIds.append(eachGamePlayedByUser)

	userGamesSet = set(gameIds)
	# Find common games for the two users
	for gameid in oppoGames:
		if gameid in userGamesSet:
			commonGames.append(gameid)

	noOfWins = noOfLosses = noOfDraws = 0
	for eachGameId in commonGames:		
		# Retrieve complete details about the game
		allQuestionsInGame = FC.query.filter(FC.gameId == eachGameId).all()
		noOfQuestionsCorrectUser, noOfQuestionsCorrectOpponent = findNumOfQuesEachUserInGameGotCorrect(
																		allQuestionsInGame, userid)
		noOfWins, noOfDraws, noOfLosses = updateWinDrawLossStat(noOfQuestionsCorrectUser, 
									noOfQuestionsCorrectOpponent, noOfWins, noOfDraws, noOfLosses)

	numPlayed = noOfDraws + noOfWins + noOfLosses
	return json.dumps({'#Played': numPlayed, 
				'#Wins': noOfWins, 
				'#Losses': noOfLosses, 
				'#Draws': noOfDraws,
				'CommonGames': commonGames})



# Returns stats of a particular game
# These stats are such provided such that the 
# results page can be replicated without any problem
def getGameStats(userid, gameidForStats):
	questionsInGame = FC.query.filter(FC.gameId == gameidForStats).all()
	opponentUserId = ""
	gameResult = ""

	noOfQuestions = 0
	noOfQuestionsCorrectUser, noOfQuestionsCorrectOpponent = findNumOfQuesEachUserInGameGotCorrect(
																		allQuestionsInGame, userid)

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
	
	noOfWins = noOfLosses = noOfDraws = 0

	for eachGamePlayed in allGamesUserPlayed:
		eachGameId = eachGamePlayed.gameId
		allQuestionsInGame = FC.query.filter(FC.gameId == eachGameId).all()
		
		noOfQuestionsCorrectUser = 0
		noOfQuestionsCorrectOpponent = 0
		for row in allQuestionsInGame:
			if row.user == userid:
				if row.flashcardId == row.userAns:
					# Check if ans is correct
					noOfQuestionsCorrectUser += 1
			else:
				if row.flashcardId == row.userAns:
					# Check if ans is correct
					noOfQuestionsCorrectOpponent += 1

		noOfWins, noOfDraws, noOfLosses = updateWinDrawLossStat(noOfQuestionsCorrectUser, 
									noOfQuestionsCorrectOpponent, noOfWins, noOfDraws, noOfLosses)

	numPlayed = noOfDraws + noOfWins + noOfLosses
	return json.dumps({'#Played': numPlayed, 
				'#Wins': noOfWins, 
				'#Losses': noOfLosses, 
				'#Draws': noOfDraws})