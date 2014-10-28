import uuid, json
from flask import Flask, render_template, session, request
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio

socketRooms = {}
roomReceivedAnswers = {}
defaultRoom = str(0)
roomIndex = 1


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

@socketio.on('joinroom', namespace='/test')
def joinRoom(room):
	if session['room'] == defaultRoom:
		# room = str(roomIndex)
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
		# roomIndex +=1
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

@socketio.on('clearroom', namespace='/test')
def clearRoom(room):
	room = room['room']
	if socketRooms.has_key(room) == True:
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
	if roomReceivedAnswers.has_key(room) == True:
		allAnswers = roomReceivedAnswers.get(room)
		# Try to group ansData based on questionId and clientId
		allAnswers.append(ansData)
		roomReceivedAnswers[room] = allAnswers
		sendReceivedAnswersToClient(room)
	else:
		allAnswers = []
		allAnswers.append(ansData)
		roomReceivedAnswers[room] = allAnswers

def sendReceivedAnswersToClient(room):
	dataToSend = roomReceivedAnswers.get(room)
	emit('my response', {'data': json.dumps(dataToSend)}, room=room)
	del roomReceivedAnswers[room]