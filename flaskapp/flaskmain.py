from flask import Flask
from Quizletauth import quizletauth

app = Flask(__name__)
app.register_blueprint(quizletauth)

if __name__ == "__main__":
	#app.debug = True
	app.run()