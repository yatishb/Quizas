import uuid
from flask import Flask, render_template, session, request
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio

socketRooms = {}
defaultRoom = str(0)
roomIndex = 1


@socketio.on('connect', namespace='/test')
def socketConnect():
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




# @socketio.on('client name', namespace='/test')
# def test_message(message):
# 	session['user'] = message['username']
# 	emit('my response', {'data': message['username'] + message['data']})

# @socketio.on('my event', namespace='/test')
# def test_message(message):
#     emit('my response', {'data': message['data']})

# @socketio.on('my broadcast event', namespace='/test')
# def test_message(message):
#     emit('my response', {'data': message['data']}, broadcast=True)

# @socketio.on('join', namespace='/test')
# def on_join(data):
#     room = data['room']
#     join_room(room)
#     if socketRooms.has_key(room) == True :
#         usersInRoom = socketRooms.get(room)
#         usersInRoom.append(session['id'])
#         socketRooms[room] = usersInRoom
#     else:
#         usersInRoom = []
#         usersInRoom.append(session['id'])
#         socketRooms[room] = usersInRoom
# 	clientName = session['user']
# 	emit('my response', {'data' : clientName + ' has entered the room ' + room}, room=room)

# @socketio.on('leave', namespace='/test')
# def on_leave(data):
#     # username = data['username']
#     room = data['room']
#     leave_room(room)
#     if socketRooms.has_key(room) == True:
#         usersInRoom = socketRooms.get(room)
#         usersInRoom.remove(session['id'])
#         socketRooms[room] = usersInRoom
#     clientName = session['user']
#     emit('my response', {'data' : clientName + ' has left the room ' + room}, room=room)

# @socketio.on('my room event', namespace='/test')
# def on_leave(message):
#     room = message['room']
#     clientName = session['user']
#     flag = 0
#     if socketRooms.has_key(room) == True:
#         usersInRoom = socketRooms.get(room)
#         for eachUser in usersInRoom:
#             if eachUser == session['id'] :
#                 flag = 1
#                 emit('my response', {'data' : clientName + ' : ' + message['data']}, room=room)
#                 break
#     else:
#         emit('my response', {'data' : "Not part of room"})
#     if flag == 0:
#         emit('my response', {'data' : "Not part of room"})

# @socketio.on('send client', namespace='/test')
# def test_message(message):
#     sendToClient = message['client']
#     for sessid, socket in request.namespace.socket.server.sockets.items():
#         # emit('my response', {'data': 'sessions name ' + socket['/test'].session['id']})
#         if socket['/test'].session['id'] == sendToClient:
#             socket['/test'].base_emit('my response', {'data': message['data']})