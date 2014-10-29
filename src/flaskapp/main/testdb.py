import json
from models import User
from . import main
from .. import db

@main.route("/modelstest/<username>")
def modelCreate(username):
	admin = User(username, username + '@example.com')
	db.session.add(admin)
	db.session.commit()
	return json.dumps("Operation performed")

@main.route("/modelsearch/<username>")
def modelCheck(username):
	db.create_all()
	users = User.query.filter_by(username = username).all()
	return json.dumps(users[0].email)