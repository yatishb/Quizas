from flask import Flask
from Quizletauth import quizletauth

app = Flask(__name__)
app.register_blueprint(quizletauth)

@app.route("/")
def running():
	return "Flask App Running"

if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')
