import json
from models import User
from . import main
from .. import db

def createDB():
	db.create_all()

@main.route("/modelstest/<username>")
def modelCreate(username):
	db.create_all()
	admin = User(username, username + '@example.com')
	db.session.add(admin)
	db.session.commit()
	users = User.query.filter_by(username = username).all()
	return json.dumps(users[0].email)