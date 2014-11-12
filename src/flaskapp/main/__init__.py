from flask import Blueprint

main = Blueprint('main', __name__)

import facebookauth
import twitterauth
import quizletauth
import quizletsets
import flaskmain
import sockets
import models
import accessdb
import statistics
import testdb
