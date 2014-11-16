from models import User, FlashGame as FG, FlashCardInGame as FC, PointsTable as PT
from sqlalchemy import func, and_
from . import main
from .. import db, redis
import json, uuid
import authhelper

# To serialise datetime to JSON
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


# Parameters: room, user1, user2, redis.hgetall(HASH_USER1), redis.hgetall(HASH_USER2), 
#             flashsetid, redis.hgetall(HASH_TIME1),redis.hgetall(HASH_TIME2)
# user1 and user2 are integers
# redis.hgetall(HASH_USER1) gives dict of FlashcardID and UserAnswer
# redis.hgetall(HASH_TIME1) gives dict of FlashcardID and Time taken by user as a string
# The equivalent parameter for that is userAns1
def documentGame(room, user1, user2, userAns1, userAns2, flashsetId, timeTaken1, timeTaken2) :
	# Store game header in FlashGame db
	gameUser1 = FG(room, flashsetId, user1)
	gameUser2 = FG(room, flashsetId, user2)
	db.session.add(gameUser1)
	db.session.add(gameUser2)

	allQuestions = userAns1.keys()

	points1 = 0
	points2 = 0

	for questionId in allQuestions:
		user1AnsChosen = userAns1.get(questionId)
		user2AnsChosen = userAns2.get(questionId)
		time1 = int(timeTaken1.get(questionId))
		time2 = int(timeTaken2.get(questionId))
		points1 += 1.0*(10000 - time1) / 1000
		points2 += 1.0*(10000 - time2) / 1000

		# -1 refers to time taken by client for each answer
		cardUser1 = FC(room, flashsetId, questionId, user1, user1AnsChosen, time1)
		cardUser2 = FC(room, flashsetId, questionId, user2, user2AnsChosen, time2)
		db.session.add(cardUser1)
		db.session.add(cardUser2)

	# Update points for both users
	pointsRow1 = PT.query.filter(PT.id == user1).first()
	pointsRow2 = PT.query.filter(PT.id == user2).first()
	pointsRow1.points += int(points1)
	pointsRow2.points += int(points2)

	db.session.commit()


# Used for Single Player, and Challenges.
def soloGameResultsWriteDbWithGameId(userid, gameId, receivedData) :
	flashsetId = receivedData['flashset']
	cards = receivedData['cards']
	pointsScored = 0

	gameUser = FG(gameId, flashsetId, userid)
	db.session.add(gameUser)

	for eachQues in cards:
		questionId = eachQues['flashcard']
		userAns = eachQues['result']
		time = eachQues['time']
		pointsScored += 1.0*(10000 - time) / 1000
		cardUser = FC(gameId, flashsetId, questionId, userid, userAns, time)
		db.session.add(cardUser)

	pointsRow = PT.query.filter(PT.id == userid).first()
	pointsRow.points += int(pointsScored)
	db.session.commit()

	# Return gameId so challenges can make use of it.
	return gameId


def soloGameResultsWriteDb(userid, receivedData) :
	gameId = str(uuid.uuid1())
	return soloGameResultsWriteDbWithGameId(userid, gameId, receivedData)


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
	return json.dumps({'played': numPlayed, 
				'wins': noOfWins, 
				'losses': noOfLosses, 
				'draws': noOfDraws})
	


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
	return json.dumps({'played': numPlayed, 
				'wins': noOfWins, 
				'losses': noOfLosses, 
				'draws': noOfDraws,
				'commongames': commonGames})



# Returns stats of a particular game
# These stats are such provided such that the 
# results page can be replicated without any problem
def getGameStats(userid, gameidForStats):
	game = FG.query.filter(FG.gameId == gameidForStats, FG.user != userid).first()

	if game == None:
		request = make_response('Game not found', 401)
		return request

	questionsInGame = FC.query.filter(FC.gameId == gameidForStats).all()
	gameResult = ""

	noOfQuestions = 0
	flashcards = []
	time = oppTime = 0

	# Create array flashcards which shows the cards and answers
	for row in questionsInGame:

		if row.user == userid:
			noOfQuestions += 1
			flag = False

			# Check if the flashcard array already contains the question.
			# If this is so then the enemy's answers has already been recorded in array
			for i in range(0, len(flashcards)):
				if flashcards[i].get('question') == row.flashcardId:
					flag = True
					eachQues = flashcards[i]
					eachQues['ans'] = row.userAns
					eachQues['time'] = row.time
					flashcards[i] = eachQues
					
			# Could not find the question in the array so hence create new dict and add it
			if flag == False:
				eachQues = {}
				eachQues['question'] = row.flashcardId
				eachQues['ans'] = row.userAns
				eachQues['time'] = row.time
				flashcards.append(eachQues)
		else:
			flag = False
			# Check if the flashcard array already contains the question.
			# If this is so then the user's answers has already been recorded in array
			for i in range(0, len(flashcards)):
				if flashcards[i].get('question') == row.flashcardId:
					flag = True
					eachQues = flashcards[i]
					eachQues['enemy'] = row.userAns
					eachQues['enemytime'] = row.time
					flashcards[i] = eachQues

			# Could not find the question in the array so hence create new dict and add it
			if flag == False:
				eachQues = {}
				eachQues['question'] = row.flashcardId
				eachQues['enemy'] = row.userAns
				eachQues['enemytime'] = row.time
				flashcards.append(eachQues)

	# To get the other relevant data
	datetime = game.datetime
	flashset = game.flashsetId
	opponentUserId = authhelper.lookupInternal(game.user)

	noOfQuestionsCorrectUser, noOfQuestionsCorrectOpponent = findNumOfQuesEachUserInGameGotCorrect(
																		questionsInGame, userid)

	if noOfQuestionsCorrectUser > noOfQuestionsCorrectOpponent:
		gameResult = "Won"
	elif noOfQuestionsCorrectUser < noOfQuestionsCorrectOpponent:
		gameResult = "Lost"
	else:
		gameResult = "Drew"

	return json.dumps({"questions":noOfQuestions, 
				"correct":noOfQuestionsCorrectUser, 
				"againstUser":opponentUserId, 
				"againstCorrect":noOfQuestionsCorrectOpponent, 
				"result":gameResult,
				"flashset":flashset,
				"flashcards":flashcards,
				"datetime":datetime}, default=date_handler)



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
