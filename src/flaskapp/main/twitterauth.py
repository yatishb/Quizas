# Adapted from:
# http://whichlight.com/blog/twitter-oauth-in-python-with-tweepy-and-flask/

import requests
import ast
import json

# Use tweepy to manage Twitter auth stuff.
# See:
# http://tweepy.readthedocs.org/en/v2.3.0/
# Requires tweepy pip package.
import tweepy

import secrets
import authhelper
import quizletsets

from flask import Blueprint
from flask import request, redirect

# Use the main blueprint, so that the code is in general tidier.
from . import main


CONSUMER_TOKEN  = secrets.auth["twitter"]["client_id"]
CONSUMER_SECRET = secrets.auth["twitter"]["key_secret"]
CALLBACK_URL    = secrets.auth["twitter"]["redirect_url"]

# Err, should probably be using KVSession??
session = dict()
db = dict() #you can save these values to a database


@main.route("/twitterauth")
def send_token():
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN,
	                           CONSUMER_SECRET,
	                           CALLBACK_URL)
	
	try:
		# get the request tokens
		redirect_url = auth.get_authorization_url()
		session['request_token'] = (auth.request_token.key,
		                            auth.request_token.secret)
	except tweepy.TweepError:
		print 'Error! Failed to get request token'
	
	# this is twitter's url for authentication
	return redirect(redirect_url)




# The Callback
@main.route("/twitterauthstep2")
def get_verification():
	# User denied our request.
	if request.args.get("denied") != None:
		# Redirect back to homepage.
		return redirect(secrets.auth["login_failure_url"]);
	
	#get the verifier key from the request url
	verifier = request.args['oauth_verifier']
	
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
	token = session['request_token']
	del session['request_token']
	
	auth.set_request_token(token[0], token[1])

	try:
		auth.get_access_token(verifier)
	except tweepy.TweepError:
		print 'Error! Failed to get access token.'
	
	#now you have access!
	api = tweepy.API(auth)

	#store in a db
	db['api'] = api
	db['access_token_key'] = auth.access_token.key
	db['access_token_secret'] = auth.access_token.secret

	# Now Go to a page where we make use of the Twitter API.
	resp = redirect(secrets.auth["login_success_url"])

	new_userid = "twitter:" + auth.access_token.key
	if authhelper.userids_clash_userid(new_userid):
		# A different user was previously logged in on this
		# browser (i.e. different w/ different twitter acct).
		# Delete their cookies.
		for site in authhelper.auth_sites:
			if request.cookies.get(site + "_user_id") != None:
				resp.set_cookie(site + "_user_id", '', expires = 0)

	# See http://tweepy.readthedocs.org/en/v2.3.0/auth_tutorial.html#oauth-authentication
	resp.set_cookie("twitter_user_id", auth.access_token.key);
	resp.set_cookie("twitter_access_token", auth.access_token.secret);
	# resp.set_cookie("twitter_expires_in", "???"); # Twitter tokens don't expire

	# Ensure user table has an internal id.
	authhelper.register(new_userid)
	quizletsets.ensure_some_flashsets(new_userid)

	return resp


# Get Twitter username + profile picture url.
# See: https://dev.twitter.com/rest/reference/get/users/show
# probably only want to be application-only request.
# See https://dev.twitter.com/oauth/application-only
@main.route("/profile/twitter/<twitter_id>")
def get_twitter_profile(twitter_id):
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN,
	                           CONSUMER_SECRET,
	                           CALLBACK_URL)
	
	# What about client requests
	api = tweepy.API(auth)
	user = api.get_user(twitter_id)

	return json.dumps({"name": user.name,
	                   "picture": user.profile_image_url})


