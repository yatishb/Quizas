import os
from flask import Flask
from quizletauth import quizletauth

app = Flask(__name__)
app.register_blueprint(quizletauth)

# Generate a secret random key for the session
# We need this for sessions
app.secret_key = os.urandom(24)

@app.route("/")
def running():
	return "Flask App Running"

if __name__ == "__main__":
	app.debug = True
	# app.run(host='0.0.0.0')
	app.run(host="dev.localhost")
