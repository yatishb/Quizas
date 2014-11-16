import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, ColumnDefault, sql
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
	flashsetId = db.Column(db.String(40))
	user = db.Column(db.Integer)
	datetime = db.Column(db.DateTime, default = datetime.datetime.utcnow())

	__tablename__ = "FlashGame"
	def __init__(self, gameId, flashsetId, user):
		self.gameId = gameId
		self.flashsetId = flashsetId
		self.user = user 

	def __repr__(self):
		return '<Game ID %r>' % self.gameId	


class FlashCardInGame(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gameId = db.Column(db.String(40))
	flashsetId = db.Column(db.String(40))
	flashcardId = db.Column(db.String(40))
	user = db.Column(db.Integer)
	userAns = db.Column(db.String(40))
	time = db.Column(db.Integer) # time is in msec

	__tablename__ = "FlashCardInGame"
	def __init__(self, gameId, flashsetId, flashcardId, user, userAns, time):
		self.gameId = gameId
		self.flashsetId = flashsetId
		self.flashcardId = flashcardId
		self.user = user
		self.userAns = userAns
		self.time = time

	def __repr__(self):
		return '<Game ID %r FlashCardId %r User %r>' % (self.gameId, self.flashcardId, self.user)


# Table for which (Quizlet) Flashsets the user has added
# with our Quizas app.
class UserFlashSet(db.Model):
	# Because we need ID.
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.Integer)
	flashsetId = db.Column(db.String(40))

	# Constraint so each row is unique
	# See http://docs.sqlalchemy.org/en/latest/core/constraints.html
	__tablename__ = "UserFlashSet"
	__table_args__ = (
			UniqueConstraint("user", "flashsetId"),
			)

	def __init__(self, user, flashsetId):
		self.user = user
		self.flashsetId = flashsetId

	def __repr__(self):
		return '<UserFlashSet %r %r>' % (self.gameId, self.flashsetId)


class UserChallenge(db.Model):
	challengerId = db.Column(db.Integer)
	recipientId  = db.Column(db.Integer)
	gameId       = db.Column(db.String(40), primary_key = True)
	status       = db.Column(db.String(80))

	__tablename__ = "UserChallenge"
	def __init__(self, challengerId, recipientId, gameId, status):
		self.challengerId = challengerId
		self.recipientId = recipientId
		self.gameId = gameId
		self.status = status

	def __repr__(self):
		return '<UserChallenge %r %r %r %r>' % (self.challengerId,
		                                        self.recipientId,
		                                        self.gameId,
		                                        self.status)


class QuestionsChallenge(db.Model):
	gameId = db.Column(db.String(40), primary_key = True)
	questions = db.Column(db.String(5000))

	__tablename__ = "QuestionsChallenge"
	def __init__(self, gameId, questions):
		self.gameId = gameId
		self.questions = questions

	def __repr__(self):
		return '<QuestionsChallenge %r %r>' % (self.gameId, self.questions)


class PointsTable(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	points = db.Column(db.Integer)

	__tablename__ = "PointsTable"
	def __init__(self, uid, points):
		self.id = uid
		self.points = points

	def __repr__(self):
		return '<PointsTable %r %r>' % (self.id, self.points)



class InternalUserAuth(db.Model):
	# Because we need ID.
	id = db.Column(db.Integer)
	user_id = db.Column(db.String(80), primary_key=True)

	__tablename__ = "InternalUserAuth"
	def __init__(self, user):
		self.user_id = user

	def __repr__(self):
		return '<InternalUser %r %r>' % (self.id, self.user_id)

InternalUserAuth.__table__.c.id.default = ColumnDefault(sql.select([sql.func.coalesce(sql.func.max(InternalUserAuth.id) + 1, 1)]).as_scalar())

