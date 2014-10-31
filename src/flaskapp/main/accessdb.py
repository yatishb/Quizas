from models import User, FlashGame, FlashCardInGame
from . import main
from .. import db

def documentGame(room, roomClientAnswers, flashsetId) :
	allQuestions = roomClientAnswers.items()
	userNames = allQuestions[0][1].keys()
	user1 = userNames[0]
	user2 = userNames[1]
	game = FlashGame(room, flashsetId, user1, user2)
	db.session.add(game)

	for eachQues in allQuestions:
		questionId = eachQues[0]
		bothClientResp = eachQues[1]
		user1Ans = bothClientResp[user1]
		user2Ans = bothClientResp[user2]
		user1Correct = True # Must check whether ans is correct
		user2Correct = True # Must check whether ans is correct

		card = FlashCardInGame(room, flashsetId, questionId, user1Ans, user2Ans, user1Correct, user2Correct)
		db.session.add(card)

	db.session.commit()