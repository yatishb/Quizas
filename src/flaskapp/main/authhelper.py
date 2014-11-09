import requests
import ast
import json

import secrets

from models import InternalUserAuth
from flask import request, redirect, abort
from . import main
from .. import db


# From user_id `site:auth_id` to internal id
# or None if the given userid isn't in the table
def lookup(userid):
	u = InternalUserAuth.query.filter_by(user_id = userid).first()
	
	if u == None:
		return None
	else:
		return u.id


# From internal id to user_id `site:auth_id
# or None if the given userid isn't in the table
def lookupInternal(internalid):
	u = InternalUserAuth.query.filter_by(id = internalid).first()
	
	if u == None:
		return None
	else:
		return u.user_id



# Returns an array of all the user_ids (`site:auth_id`),
# which the requests sends as cookies.
def get_cookie_user_ids():
	# We only have support for quizlet, twitter at this stage.
	# This is an unfortunately magic way of checking this. :/
	auth_sites = ["quizlet", "twitter"]

	cookie_names = [site + "_user_id" for site in auth_sites]
	user_ids = [site + ":" + request.cookies.get(site + "_user_id")
	            for site in auth_sites
	            if request.cookies.get(site + "_user_id") != None]

	return user_ids


# Returns internal id if they're in the database;
# or, returns None if they aren't in the DB.
# (Aside from the OAuth callback, this shouldn't return None).
def get_current_id():
	# We guarantee that if a user is logged in with something,
	# then that user id will have an entry in the relevant DB table.
	uids = get_cookie_user_ids()
	
	if len(uids) == 0:
		return None
	else:
		return lookup(uids[0])


# Adds the given userid into the database,
# assigning it a new id.
def insert_new_id(new_userid):
	# First check to make sure that the userid doesn't exist
	# in the DB already.
	# If it does, they've signed in previously. So, just keep track of
	# them using the same ID they had before.
	# (TODO: This *might* get messy if the user fucks around with different
	#  accounts. >.<).

	if lookup(new_userid) != None:
		# pk exists in DB already.
		return

	newUserAuth = InternalUserAuth(new_userid)
	db.session.add(newUserAuth)
	db.session.commit()


def link_with_current_accounts(uid, new_userid):
	newUserAuth = InternalUserAuth(new_userid)
	newUserAuth.id = uid
	db.session.add(newUserAuth)
	db.session.commit()


# Put the given userid in the database if
# i) it's not in the DB already
# and deal with the id appropriately.
def register(userid):
	uid = get_current_id()

	if uid == None:
		insert_new_id(userid)
	else:
		link_with_current_accounts(uid, userid)


# TODO:
# The missing case is if, say, user logs out with everything,
# and then logs in with a new site he hasn't logged in with before,
# then logs in with a site he used previously.
