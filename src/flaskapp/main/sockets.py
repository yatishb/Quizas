import uuid, json
from flask import Flask, render_template, session, request
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio
import accessdb, authhelper

socketRooms = {}
roomClientAnswers = {}
roomSendAnswers = {}
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
		user1 = authhelper.lookup(user1)
		user2 = authhelper.lookup(user2)

		for sessid, socket in request.namespace.socket.server.sockets.items():
			if (socket['/test'].session['id'] == user1) | (socket['/test'].session['id'] == user2):
				if socket['/test'].session['room'] == defaultRoom:
					socket['/test'].session['room'] = room
					socket['/test'].join_room(room)
					
					if socketRooms.has_key(room) == True :
						usersInRoom = socketRooms.get(room)
						usersInRoom.append(socket['/test'].session['id'])
						socketRooms[room] = usersInRoom
					else:
						usersInRoom = []
						usersInRoom.append(socket['/test'].session['id'])
						socketRooms[room] = usersInRoom
					socket['/test'].base_emit('my response', {'data': 'Joined room'})
				
				else:
					emit('my response', {'data': 'Already part of a room'})

	else:
		emit('my response', {'data': 'One or more user is incorrect'})



# End of quiz
# Clear the room
# Update answers received by the clients to db
@socketio.on('clearroom', namespace='/test')
def clearRoom():
	room = session['room']
	if socketRooms.has_key(room) == True:
		# Write all answers to db first
		# Get flashsetid here first
		# Verify if quiz is genuinely completed. If not do not write to db
		if roomClientAnswers.has_key(room) == True:
			accessdb.documentGame(room, roomClientAnswers.get(room), 1)
			del roomClientAnswers[room]

		usersInRoom = socketRooms.get(room)
		del socketRooms[room]

		for eachUser in usersInRoom :
			for sessid, socket in request.namespace.socket.server.sockets.items():
				if socket['/test'].session['id'] == eachUser:
					socket['/test'].session['room'] = defaultRoom
					socket['/test'].leave_room(room)
					socket['/test'].base_emit('my response', {'data': "cleared room"})
		# emit('my response', {'data': "checking for room"}, room=room) # This doesn't send message to any client. Verified
	else:
		emit('my response', {'data': 'no such room'})
	# This is to counter some error experienced
	session['room'] = defaultRoom


# Each response by the client for each question is handled here
@socketio.on('readanswer', namespace='/test')
def readAnswerByClient(message):
	room = session['room']
	idClient = session['id']
	idQuestion = message['qid']
	clientAnswer = message['answer']
	ansData = {}
	ansData['client'] = idClient
	ansData['question'] = idQuestion
	ansData['answer'] = clientAnswer
	print (ansData)
	if roomClientAnswers.has_key(room) == True:
		# Received replied from this room
		roomArray = roomClientAnswers.get(room)
		print ("Got into this1")
		if roomArray.has_key(idQuestion) == True:
			print ("Got into this2")
			# This question has been encountered 
			# atleast one client has already answered
			qidArray = roomArray.get(idQuestion)
			if qidArray.has_key(idClient) == False:
				qidArray[idClient] = clientAnswer
				# Also remember this answer to be sent later
				allAnswers = roomSendAnswers.get(room)
				allAnswers.append(ansData)
				roomSendAnswers[room] = allAnswers
				sendReceivedAnswersToClient(room)
		else:
			# This question hasn't been encountered
			qidArray = {}
			qidArray[idClient] = clientAnswer
			roomArray[idQuestion] = qidArray
			# Also remember this answer to be sent later
			allAnswers = []
			allAnswers.append(ansData)
			roomSendAnswers[room] = allAnswers
	else:
		# This room hasn't been encountered
		# Quiz in this room has just started
		qidArray = {}
		qidArray[idClient] = clientAnswer
		roomArray = {}
		roomArray[idQuestion] = qidArray
		roomClientAnswers[room] = roomArray
		# Also remember this answer to be sent later
		allAnswers = []
		allAnswers.append(ansData)
		roomSendAnswers[room] = allAnswers
		print ("Got into this")


# This function sends responses to both clients to proceed to next question
# Is called only when the server has received a response 
# from both clients for the same question
def sendReceivedAnswersToClient(room):
	print ("gets in here")
	dataToSend = roomSendAnswers.get(room)
	emit('my response', {'data': json.dumps(dataToSend)}, room=room)
	del roomSendAnswers[room]


#################################################################
# These functions might would not need to be called by the client

# room = str(uuid.uuid1())
# This has to be chosen by a separate function
# and then passed onto this function
@socketio.on('joinroom', namespace='/test')
def joinRoom(room):
	if session['room'] == defaultRoom:
		room = room['room']
		session['room'] = room
		join_room(room)
		if socketRooms.has_key(room) == True :
			usersInRoom = socketRooms.get(room)
			usersInRoom.append(session['id'])
			socketRooms[room] = usersInRoom
		else:
			usersInRoom = []
			usersInRoom.append(session['id'])
			socketRooms[room] = usersInRoom
		emit('my response', {'data': 'Joined room'})
	else:
		emit('my response', {'data': 'Already part of a room'})

@socketio.on('leaveroom', namespace='/test')
def leaveRoom():
	if session['room'] != defaultRoom:
		room = session['room']
		leave_room(room)
		if socketRooms.has_key(room) == True:
			usersInRoom = socketRooms.get(room)
			usersInRoom.remove(session['id'])
			socketRooms[room] = usersInRoom
		session['room'] = defaultRoom
		emit('my response', {'data': 'left room '+room})
	else:
		emit('my response', {'data': 'wasn\'t part of a room'})
