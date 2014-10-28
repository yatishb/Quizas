from flask import Blueprint

main = Blueprint('main', __name__)

import twitterauth
import quizletauth
import quizletsets
import flaskmain, sockets
