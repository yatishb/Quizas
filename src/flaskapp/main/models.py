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

# Having a single user by row means redundant data
# This going to lead to more space usage but possible reduction in query time
class FlashGame(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gameId = db.Column(db.String(40))
	flashsetId = db.Column(db.Integer)
	user = db.Column(db.String(80))

	def __init__(self, gameId, flashsetId, user):
		self.gameId = gameId
		self.flashsetId = flashsetId
		self.user = user

	def __repr__(self):
		return '<Game ID %r>' % self.gameId	


class FlashCardInGame(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gameId = db.Column(db.String(40))
	flashsetId = db.Column(db.Integer)
	flashcardId = db.Column(db.Integer)
	user = db.Column(db.String(80))
	userAns = db.Column(db.String(40))
	isCorrect = db.Column(db.Boolean)

	def __init__(self, gameId, flashsetId, flashcardId, user, userAns, isCorrect):
		self.gameId = gameId
		self.flashsetId = flashsetId
		self.flashcardId = flashcardId
		self.user = user
		self.userAns = userAns
		self.isCorrect = isCorrect

	def __repr__(self):
		return '<Game ID %r FlashCardId %r User %r>' % (self.gameId, self.flashcardId, self.user)