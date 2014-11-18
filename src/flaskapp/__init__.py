from redis import Redis
from flask import Flask
from flask.ext.socketio import SocketIO
from flask.ext.sqlalchemy import SQLAlchemy

import os, json

socketio = SocketIO()
db = SQLAlchemy()
redis = Redis()

# Open up `secrets.json` which is in the same directory as `secrets.py`.
# "Repeating yourself". Yes, it's inelegant.
# But so is using __init__.py, and having a child __init__.py depend on
#  modules which depend on this __init.py. FUCK CIRCULARITY.
# So, either we move `secrets` to a parent module, and change it in every other
#  file it's been used; OR we just innocently COPY PASTE this.
# The Right Way (TM) would be to manage blueprints not with main/__init__.py,
#  I think. (At least, not have create_app, which depends on other things, in
#  a fundamental module like __init__.py, which other things depend on...).
secrets_file = open(os.path.join(os.path.dirname(__file__),'main/secrets.json'),'r')
auth = json.load(secrets_file)
secrets_file.close()
database_uri = auth['database_uri']

def create_app(debug=False):
	"""Create an application."""
	app = Flask(__name__)
	app.debug = debug
	app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
	app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	socketio.init_app(app)
	db.init_app(app)
	# Adopted from : http://stackoverflow.com/questions/19437883/when-scattering-flask-models-runtimeerror-application-not-registered-on-db
	with app.app_context():
		# Extensions like Flask-SQLAlchemy now know what the "current" app
		# is while within this block. Therefore, you can now run........
		db.create_all()

	return app
