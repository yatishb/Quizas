from flask.ext.sqlalchemy import SQLAlchemy
from .. import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


class FlashGame(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gameId = db.Column(db.String(40), unique=True)
	flashsetId = db.Column(db.Integer)
	user1 = db.Column(db.String(20))
	user2 = db.Column(db.String(20))
	questionsArray = db.Column(db.String(100))

	def __init__(self, gameId, flashsetId, user1, user2, questionsArray):
		self.gameId = gameId
		self.flashsetId = flashsetId
		self.user1 = user1
		self.user2 = user2
		self.questionsArray = questionsArray

	def __repr__(self):
		return '<Game ID %r>' % self.gameId


class FlashCardInGame(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gameId = db.Column(db.String(40), unique=True)
	flashsetId = db.Column(db.Integer)
	flashcardId = db.Column(db.Integer)
	user1Ans = db.Column(db.String(20))
	user2Ans = db.Column(db.String(20))

	def __init__(self, gameId, flashsetId, flashcardId, user1Ans, user2Ans):
		self.gameId = gameId
		self.flashsetId = flashsetId
		self.flashcardId = flashcardId
		self.user1 = user1Ans
		self.user2 = user2Ans

	def __repr__(self):
		return '<Game ID %r FlashCardId %r>' % (self.gameId, self.flashcardId)