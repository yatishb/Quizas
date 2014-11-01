from models import User, FlashGame, FlashCardInGame
from . import main
from .. import db

def documentGame(room, roomClientAnswers, flashsetId) :
	allQuestions = roomClientAnswers.items()
	userNames = allQuestions[0][1].keys()
	user1 = userNames[0]
	user2 = userNames[1]
	gameUser1 = FlashGame(room, flashsetId, user1)
	gameUser2 = FlashGame(room, flashsetId, user2)
	db.session.add(gameUser1)
	db.session.add(gameUser2)

	for eachQues in allQuestions:
		questionId = eachQues[0]
		bothClientResp = eachQues[1]
		user1Ans = bothClientResp[user1]
		user2Ans = bothClientResp[user2]
		user1IsCorrect = True # Must check whether ans is correct
		user2IsCorrect = True # Must check whether ans is correct

		cardUser1 = FlashCardInGame(room, flashsetId, questionId, user1, user1Ans, user1IsCorrect)
		cardUser2 = FlashCardInGame(room, flashsetId, questionId, user2, user2Ans, user2IsCorrect)
		db.session.add(cardUser1)
		db.session.add(cardUser2)

	db.session.commit()


def getUserWinLossStats(userid):
	# Find all games where either user1 or user2 is userid
	# Retrieve all cards for each game and individually compute if userid won
	return userid
