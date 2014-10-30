import uuid, json
from flask import Flask, render_template, session, request
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio

socketRooms = {}
roomClientAnswers = {}
roomSendAnswers = {}
defaultRoom = str(0)


@socketio.on('connect', namespace='/test')
def socketConnect():
	# Could substitute id with some cookie user variable
    session['id'] = str(uuid.uuid4())
    session['room'] = defaultRoom
    emit('my response', {'data': 'Connected ' + session['id']})

@socketio.on('disconnect', namespace='/test')
def socketDisconnect():
    print('Client disconnected')

@socketio.on('print connected', namespace='/test')
def printSocketsConnected():
	for sessid, socket in request.namespace.socket.server.sockets.items():
		emit('my response', {'data': 'sessions uuid: ' + socket['/test'].session['id']})


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


# End of quiz
# Clear the room
# Update answers received by the clients to db
@socketio.on('clearroom', namespace='/test')
def clearRoom():
	room = session['room']
	if socketRooms.has_key(room) == True:
		usersInRoom = socketRooms.get(room)
		del socketRooms[room]
		for eachUser in usersInRoom :
			for sessid, socket in request.namespace.socket.server.sockets.items():
				if socket['/test'].session['id'] == eachUser:
					socket['/test'].session['room'] = defaultRoom
					socket['/test'].leave_room(room)
					socket['/test'].base_emit('my response', {'data': "cleared room"})
		emit('my response', {'data': "checking for room"}, room=room) # This doesn't send message to any client. Verified
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
	if roomClientAnswers.has_key(room) == True:
		# Received replied from this room
		roomArray = roomClientAnswers.get(room)
		if roomArray.has_key(idQuestion) == True:
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


# This function sends responses to both clients to proceed to next question
# Is called only when the server has received a response 
# from both clients for the same question
def sendReceivedAnswersToClient(room):
	dataToSend = roomSendAnswers.get(room)
	emit('my response', {'data': json.dumps(dataToSend)}, room=room)
	del roomSendAnswers[room]