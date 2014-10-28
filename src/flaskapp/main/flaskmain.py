from flask import Flask, render_template
from . import main

@main.route("/")
def running():
	return "Flask App Running"

@main.route("/sockets")
def startSocketsForm():
	return render_template('index.html')