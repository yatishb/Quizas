from models import User, FlashGame as FG, FlashCardInGame as FC
from sqlalchemy import func, and_
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
	                              filter_by(user=userid).\
	                              group_by(FG.gameId).\
	                              having(FG.flashsetId == setid)
	gameIds = [g.gameId for g in allGamesUserPlayed]
	noOfWins = 0
	noOfLosses = 0
	noOfDraws = 0

	# Look through these games for # W/L/D
	# based on the flashset.
	for eachGamePlayed in allGamesUserPlayed:
		eachGameId = eachGamePlayed.gameId
		allQuestionsInGame = FC.query.filter_by(gameId = eachGameId).all()

		# This is written in a very imperative style!

		noOfQuestionsCorrectUser = 0
		noOfQuestionsCorrectOpponent = 0
		for row in allQuestionsInGame:
			rowIsCorrect = row.flashcardId == row.userAns
			if row.user == userid:
				if rowIsCorrect:
					noOfQuestionsCorrectUser += 1
			else:
				if rowIsCorrect:
					noOfQuestionsCorrectOpponent += 1

		if noOfQuestionsCorrectUser > noOfQuestionsCorrectOpponent:
			noOfWins += 1
		elif noOfQuestionsCorrectUser < noOfQuestionsCorrectOpponent:
			noOfLosses += 1
		else:
			noOfDraws += 1


	# For this, we want to get all the flashcardIds
	# where user==user_id and flashsetId==set_id
	flashCardRows = FC.query.filter_by(user = userid,
	                                   flashsetId = setid).all()
	
	# Gather the flashCardIds which were tested.
	flashCardIds = set([fc.flashcardId for fc in flashCardRows])
	# Gather user answers per flashcardId
	# answerForUser : dict{ fcid -> [user answers for those] }
	userAnswers = dict([(fcid,
	                     [row.userAns
	                      for row in flashCardRows
	                      if row.flashcardId == fcid])
	                    for fcid in flashCardIds])
	# Gather the correct/total stats for each flashcardId
	# flashCardStats : dict{ fcid -> {"correct": int, "total": int} }
	# TODO: more stuff later, so there's more information as to
	# how the user is doing with the flashcard *recently*.
	flashCardStats = dict([(fcid,
	                       {"correct": userAnswers[fcid].count(fcid),
	                        "total": len(userAnswers[fcid])})
	                       for fcid in flashCardIds])


	numPlayed = noOfDraws + noOfWins + noOfLosses
	return json.dumps({'played': numPlayed,
	                   'wins': noOfWins,
	                   'losses': noOfLosses,
	                   'draws': noOfDraws,
	                   'fcids': list(flashCardIds),
	                   'gameids': gameIds,
	                   'flashcards': flashCardStats})
