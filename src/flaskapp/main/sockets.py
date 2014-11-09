import uuid, json
from flask import Flask, render_template, session, request
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio, redis
import accessdb, authhelper

defaultRoom = str(0)


@socketio.on('connect', namespace='/test')
def socketConnect():
	# Read id with some cookie user variable
	# Use this and then find internal user id
    session['id'] = authhelper.get_current_id()
    session['room'] = defaultRoom
    emit('my response', {'data': 'Connected %r' % session['id']})

@socketio.on('disconnect', namespace='/test')
def socketDisconnect():
    print('Client disconnected')

@socketio.on('print connected', namespace='/test')
def printSocketsConnected():
	for sessid, socket in request.namespace.socket.server.sockets.items():
		emit('my response', {'data': 'sessions uuid: %r' % socket['/test'].session['id']})




# Client sends the names of the two users that are supposed to form the room
# Socket reads the two usernames and creates a room for both
@socketio.on('assignroom', namespace='/test')
def assignRoom(message):
	room = str(uuid.uuid1())
	user1 = message['user1']
	user2 = message['user2']

	if authhelper.lookup(user1) != None and authhelper.lookup(user2) != None:
		# Get the internal user ids of the clients
		user1 = authhelper.lookup(user1)
		user2 = authhelper.lookup(user2)

		for sessid, socket in request.namespace.socket.server.sockets.items():
			if (socket['/test'].session['id'] == user1) or (socket['/test'].session['id'] == user2):
				if socket['/test'].session['room'] == defaultRoom:
					socket['/test'].session['room'] = room
					socket['/test'].join_room(room)
					
					# Check redis if room exists
					# Add client to room and create room if not found
					if redis.hexists("ROOMS", room) == True :
						usersInRoom = redis.hget("ROOMS", room)
						usersInRoom += ", %r" % socket['/test'].session['id']
						redis.hset("ROOMS", room, usersInRoom)
						redis.save()
					else:
						redis.hset("ROOMS", room, socket['/test'].session['id'])
						redis.save()
					socket['/test'].base_emit('my response', {'data': 'Joined room'})
				
				else:
					emit('my response', {'data': 'Already part of a room'})

		# This is to counter the problem being faced
		if (session['id'] == user1) or (session['id'] == user2):
			session['room'] = room

	else:
		emit('my response', {'data': 'One or more user is incorrect'})



# End of quiz
# Clear the room
# Update answers received by the clients to db
@socketio.on('clearroom', namespace='/test')
def clearRoom():
	room = session['room']
	print room
	if redis.hexists("ROOMS", room) == True:
		# Read users from redis
		# Expect usersInRoom to be a list of comma separated ids
		usersInRoom = redis.hget("ROOMS", room)
		usersInRoom = usersInRoom.split(", ")
		redis.hdel("ROOMS", room)

		HASH_SEND = "ROOM_" + room + "_SEND"
		redis.pexpire(HASH_SEND, 1)


		# Write all answers to db first
		# Get flashsetid here first
		# Verify if quiz is genuinely completed. If not do not write to db
		HASH_USER1 = "ROOM_" + room + "_" + usersInRoom[0]
		HASH_USER2 = "ROOM_" + room + "_" + usersInRoom[1]
		# Check if game exists and number of questions answered are same
		if (redis.hlen(HASH_USER1) == redis.hlen(HASH_USER2) and redis.exists(HASH_USER1) == True):
			accessdb.documentGame(room, int(usersInRoom[0]), int(usersInRoom[1]), redis.hgetall(HASH_USER1), 
				redis.hgetall(HASH_USER2), 1)

		# Clear hash key from redis
		redis.pexpire(HASH_USER1, 1)
		redis.pexpire(HASH_USER2, 1)
		
		for eachUser in usersInRoom :
			# Sending expiry information to client
			for sessid, socket in request.namespace.socket.server.sockets.items():
				if socket['/test'].session['id'] == int(eachUser):
					socket['/test'].session['room'] = defaultRoom
					socket['/test'].leave_room(room)
					socket['/test'].base_emit('my response', {'data': "cleared room"})
		# emit('my response', {'data': "checking for room"}, room=room) # This doesn't send message to any client. Verified
		redis.save()
	else:
		emit('my response', {'data': 'no such room'})
	# This is to counter some error experienced
	session['room'] = defaultRoom



# Each response by the client for each question is handled here
@socketio.on('readanswer', namespace='/test')
def readAnswerByClient(message):
	room = session['room']

	# Decode the message obtained
	idClient = session['id']
	idQuestion = message['qid']
	clientAnswer = message['answer']

	HASH_USER = "ROOM_" + room + "_" + str(idClient)
	HASH_SEND = "ROOM_" + room + "_SEND"

	# Store result in 2 separate tables in redis
	# One table is for the purpose of answer retention
	# Other table is for sending information abt other client's answer
	redis.hset(HASH_USER, idQuestion, clientAnswer)
	redis.hset(HASH_SEND, idClient, clientAnswer)
	redis.save()

	if redis.hlen(HASH_SEND) == 2:
		sendReceivedAnswersToClient(HASH_SEND, room)



# This function sends responses to both clients to proceed to next question
# Is called only when the server has received a response 
# from both clients for the same question
def sendReceivedAnswersToClient(hashSend, room):
	answersForQuestion = redis.hgetall(hashSend)
	dataToSend = {}
	clientsList = answersForQuestion.keys()
	for eachClient in clientsList:
		# Find user id of the client
		userId = authhelper.lookupInternal(eachClient)
		dataToSend[userId] = answersForQuestion.get(eachClient)
		redis.hdel(hashSend, eachClient)

	emit('my response', {'data': json.dumps(dataToSend)}, room=room)
	redis.save()
