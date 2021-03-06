import uuid, json,time
from flask import Flask, render_template, session, request
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio, redis
import internalstats, authhelper, quizletsets

defaultRoom = str(0)
NUMQUES = 10
clients = []

@socketio.on('connect', namespace='/test')
def socketConnect():
	# Read id with some cookie user variable
	# Use this and then find internal user id
    session['id'] = authhelper.get_current_id()
    session['room'] = defaultRoom
    session['random'] = str(uuid.uuid1())
    print 'Connected %r- %r' % (session['id'], session['random'])
    emit('my response', {'data': 'Connected %r- %r' % (session['id'], session['random'])})
    clients.append(request.namespace)

@socketio.on('disconnect', namespace='/test')
def socketDisconnect():
    print('Client disconnected')
    if clients.count(request.namespace) != 0:
    	clients.remove(request.namespace)

@socketio.on('print connected', namespace='/test')
def printSocketsConnected():
	for client in clients:
		emit('my response', {'data': "session id: %r random: %r" % (client.session['id'], client.session['random'])})


# Return the list of the users who are online
# Checks the sockets connected and stores all the unique ids
# These unique internal ids are matched and their actual ids are returned
@socketio.on('online users', namespace='/test')
def printSocketsConnected():
	onlineUsers = []
	onlineIDs = []
	for client in clients:
		if onlineUsers.count(client.session['id']) == 0:
			onlineUsers.append(client.session['id'])

	for eachOnlineUser in onlineUsers:
		facebookId = authhelper.lookupInternalFacebook(eachOnlineUser)
		if facebookId != None:
			onlineIDs.append( str(facebookId) )

	emit('online', {'data': onlineIDs})



# This is to send the notification of a game request to another client C2
# Read this notification and forward this request to the client C2
@socketio.on('send notification', namespace='/test')
def sendNotificationToSocket(message):
	user = message['user']
	flashset = message['set']
	userSendTo = message['opponent']

	internalUser = authhelper.lookup(user)
	internalUserOppo = authhelper.lookup(userSendTo)
	flagFoundUser = False

	# Check if internal user is the same as the id of the socket.
	# If not return failure
	if internalUser != session['id'] or internalUser == None or internalUserOppo == None:
		# return failure
		flagFoundUser = True
		gameRejection = {'rejectedby': userSendTo}
		emit('user non-existent', {'data': json.dumps(gameRejection)})
	else:
		requestUserFacebookId = authhelper.lookupInternalFacebook(internalUser)
		gameRequest = {"set": flashset, "requestfrom": requestUserFacebookId}
		for client in clients:
			if client.session['id'] == internalUserOppo:
				flagFoundUser = True
				if client.session['room'] != defaultRoom:
					gameRejection = {'rejectedby': userSendTo}
					emit('game rejected', {'data': json.dumps(gameRejection)})
				else:
					client.base_emit('game request', {'data': json.dumps(gameRequest)})

	# If user not found
	if flagFoundUser == False:
		gameRejection = {'rejectedby': userSendTo}
		emit('user not online', {'data': json.dumps(gameRejection)})


# Handle any rejection received as a response.
# Forward this rejection onto the first client who responded so
@socketio.on('reject', namespace='/test')
def gameRejected(message):
	userInitiatedReq = message['requester']
	userReceiver = message['receiver']

	internalUserInitiatedReq = authhelper.lookup(userInitiatedReq)
	gameRejection = {'rejectedby': userReceiver}
	for client in clients:
		if client.session['id'] == internalUserInitiatedReq:
			client.base_emit('game rejected', {'data': json.dumps(gameRejection)})




# Client sends the names of the two users that are supposed to form the room
# Socket reads the two usernames and creates a room for both
@socketio.on('assignroom', namespace='/test')
def assignRoom(message):
	room = str(uuid.uuid1())
	user1 = message['user1']
	user2 = message['user2']
	flashset = message['flashset']
	shuffledFlashcards = quizletsets.shuffled_flashset_json(flashset, NUMQUES)

	if authhelper.lookup(user1) != None and authhelper.lookup(user2) != None and shuffledFlashcards.has_key('error') == False:
		# Get the internal user ids of the clients
		user1 = authhelper.lookup(user1)
		user2 = authhelper.lookup(user2)


		# Store the flashsetid for room information in redis
		# This key should never exist in db. If it does something is wrong
		if redis.hexists("ROOMS_SETS", room) == False:
			redis.hset("ROOMS_SETS", room, flashset)
		# Deal with shuffled flashcards
		# Store all the flashcards json in redis as a string
		flashcardsJson = shuffledFlashcards['questions']
		usersInRoom = str(user1) + ", " + str(user2)
		redis.hset("ROOMS_CARDS", room, json.dumps(flashcardsJson))
		redis.hset("ROOMS", room, usersInRoom)
		redis.save()

		for client in clients:
			if (client.session['id'] == user1) or (client.session['id'] == user2):
				if client.session['room'] == defaultRoom:
					client.session['room'] = room
					client.base_emit('my response', {'data': 'GAME BEGINS...'})
				
				else:
					emit('my response', {'data': 'Already part of a room'})

		# This is to counter the problem being faced
		if (session['id'] == user1) or (session['id'] == user2):
			session['room'] = room

		# Send game initilization json to the clients
		# Contains information about the enemy name, pic, total num questions
		for client in clients:
			if (client.session['id'] == user1) or (client.session['id'] == user2):
				setName = quizletsets.get_flashset_name(flashset)
				gameInitData = getGameInit(client.session['id'], user1, user2, room, setName)
				client.base_emit('game accepted', {'data': json.dumps(gameInitData)})


	else:
		emit('my response', {'data': 'Either user(s) or flashset is incorrect'})


def getGameInit(user, user1, user2, room, setName):
	if user == user1:
		opponent = user2
	else:
		opponent = user1

	# oppoStats = json.loads( internalstats.getIndividualUserGameStats(opponent) )
	# if oppoStats['played'] == 0:
	# 	winpercent = 0
	# else:
	# 	winpercent = oppoStats['wins']

	# userStats = json.loads( internalstats.getIndividualUserGameStats(user) )
	# if userStats['played'] == 0:
	# 	userwinpercent = 0
	# else:
	# 	userwinpercent = userStats['wins']

	playerPoints = internalstats.getPointsPlayer(user)
	oppoPoints = internalstats.getPointsPlayer(opponent)

	headToHead = json.loads( internalstats.getCommonGamesStats(user, opponent) )
	encounter = headToHead['played']
	if encounter == 0:
		encounterwin = 0
	else:
		encounterwin = headToHead['wins']

	gameInitData = { "totalQuestions": NUMQUES, 
					 "encounterTotal": encounter, 
					 "encounterWin": encounterwin, 
					 "room":room,
					 "playerPoints": playerPoints,
					 "enemyID": authhelper.lookupInternalFacebook(opponent),
					 "enemyPoints": oppoPoints,
					 "matchName":setName}
	return gameInitData



# Read the game created beacon from the clients.
# Copy the information for one client to another socket belonging to the same client
# If this beacon is received from two users part of the same room,
# this means that the users are ready to receive the first question.
# Then send first question
@socketio.on('gameinitialised', namespace='/test')
def gameInitialisedByClient(message):
	roomShouldBe = str(message['room'])

	# Check if user part of the room
	# If so then add room information to the connection
	userPartOfRoom = False
	usersInRoom = redis.hget("ROOMS", roomShouldBe)
	usersInRoom = usersInRoom.split(", ")
	for eachUser in usersInRoom:
		if session['id'] == int(eachUser):
			userPartOfRoom = True
			break

	if userPartOfRoom == True:
		session['room'] = roomShouldBe
	else:
		emit('error', {'data' : 'INTRUDER!'})
		return

	room = session['room']
	userid = session['id']
	join_room(room)
	time.sleep(1)

	HASH_INIT = "ROOM_INIT"

	if redis.hexists(HASH_INIT, room) == True:
		if redis.hget(HASH_INIT, room) != userid:
			# Received game initiated beacons from both users
			# Delete this field from redis now
			redis.hdel(HASH_INIT, room)
			redis.save()
			# And send very first question to the room to kick-start the entire game
			sendFirstQuestionInfoToClient(room, usersInRoom)
	else:
		# This is the first beacon received.
		# Only one client is ready to play and so record it
		# Wait for the second client to get ready also
		redis.hset(HASH_INIT, room, userid)
		redis.save()



# End of quiz
# Clear the room
# Update answers received by the clients to db
@socketio.on('clearroom', namespace='/test')
def clearRoom():
	room = session['room']

	# Handle for when/if the second client
	if room == defaultRoom:
		return

	if redis.hexists("ROOMS", room) == True:
		# Read users from redis
		# Expect usersInRoom to be a list of comma separated ids
		usersInRoom = redis.hget("ROOMS", room)
		usersInRoom = usersInRoom.split(", ")
		redis.hdel("ROOMS", room)

		HASH_SEND = "ROOM_" + room + "_SEND"
		HASH_SENDTIME = "ROOM_" + room + "_SEND_TIME"
		redis.pexpire(HASH_SEND, 1)
		redis.pexpire(HASH_SENDTIME, 1)


		# Write all answers to db first
		# Get flashsetid here first
		# Verify if quiz is genuinely completed. If not do not write to db
		HASH_USER1 = "ROOM_" + room + "_" + usersInRoom[0]
		HASH_USER2 = "ROOM_" + room + "_" + usersInRoom[1]
		HASH_TIME1 = HASH_USER1 + "_TIME"
		HASH_TIME2 = HASH_USER2 + "_TIME"
		# Check if game exists and number of questions answered are same
		if (redis.hlen(HASH_USER1) == redis.hlen(HASH_USER2) and redis.exists(HASH_USER1) == True):
			internalstats.documentGame(room, int(usersInRoom[0]), int(usersInRoom[1]), redis.hgetall(HASH_USER1), 
				redis.hgetall(HASH_USER2), redis.hget("ROOMS_SETS", room), redis.hgetall(HASH_TIME1),
				redis.hgetall(HASH_TIME2))

		# Clear hash key from redis
		# Second parameter here refers to time in msec when key should expire
		# Setting expiry time as 1msec to delete the key
		redis.pexpire(HASH_USER1, 1)
		redis.pexpire(HASH_USER2, 1)
		redis.pexpire(HASH_TIME1, 1)
		redis.pexpire(HASH_TIME2, 1)
		redis.hdel("ROOMS_SETS", room)
		redis.hdel("ROOMS_CARDS", room)
		
		for eachUser in usersInRoom :
			# Sending expiry information to client
			for client in clients:
				if client.session['id'] == int(eachUser):
					client.session['room'] = defaultRoom
					client.leave_room(room)
					client.base_emit('gameOver', {'data': "GAME OVER!!"})
		# emit('my response', {'data': "checking for room"}, room=room) # This doesn't send message to any client. Verified
		redis.save()
	else:
		emit('my response', {'data': 'no such room'})
	# This is to counter some error experienced
	session['room'] = defaultRoom



# Each response by the client for each question is handled here
@socketio.on('readanswer', namespace='/test')
def readAnswerByClient(message):
	message = json.loads(message)
	room = session['room']
	idClient = session['id']

	# Decode the message obtained
	idQuestion = message['id']
	clientAnswer = message['answer']
	done = int(message['done']) # num questions including current done
	time = message['time']

	HASH_USER = "ROOM_" + room + "_" + str(idClient)
	HASH_SEND = "ROOM_" + room + "_SEND"
	HASH_SENDTIME = "ROOM_" + room + "_SEND_TIME"
	HASH_TIME = "ROOM_" + room + "_" + str(idClient) + "_TIME"

	# Store result in 2 separate tables in redis
	# One table is for the purpose of answer retention
	# Other table is for sending information abt other client's answer
	redis.hset(HASH_USER, idQuestion, clientAnswer)
	redis.hset(HASH_SEND, idClient, clientAnswer)
	redis.hset(HASH_SENDTIME, idClient, time)
	redis.hset(HASH_TIME, idQuestion, time)
	redis.save()

	if redis.hlen(HASH_SEND) == 2:
		sendNextQuesInfoToClient(HASH_SEND, HASH_SENDTIME, room, done)



# This function sends responses to both clients to proceed to next question
# Is called only when the server has received a response 
# from both clients for the same question
# This function also sends the clients the details of the next question
def sendNextQuesInfoToClient(hashSend, hashSendTime, room, done):
	answersForQuestion = redis.hgetall(hashSend)
	timeTakenByUsers = redis.hgetall(hashSendTime)
	clientsList = answersForQuestion.keys()

	commonDataToSend = getNextQuestionForRoom(room, done)

	dataToSend1 = {"player":answersForQuestion.get(clientsList[0]), "playerTime":int(timeTakenByUsers.get(clientsList[0])), 
				"enemy":answersForQuestion.get(clientsList[1]), "enemyTime":int(timeTakenByUsers.get(clientsList[1]))}
	dataToSend2 = {"player":answersForQuestion.get(clientsList[1]), "playerTime":int(timeTakenByUsers.get(clientsList[1])),
				"enemy":answersForQuestion.get(clientsList[0]), "enemyTime":int(timeTakenByUsers.get(clientsList[0]))}
	dataToSend1.update(commonDataToSend)
	dataToSend2.update(commonDataToSend)
	dataToSend = {clientsList[0]:dataToSend1, clientsList[1]:dataToSend2}

	for eachClient in clientsList:
		# For each client in game, send customized message
		for client in clients:
			if client.session['id'] == int(eachClient):
				client.base_emit('nextQuestion', {'data': json.dumps(dataToSend[eachClient])})

		# If messages have been sent to the client in the room
		# Remove the redis key-value pair for message to be sent to a client
		redis.hdel(hashSend, eachClient)
		redis.hdel(hashSendTime, eachClient)

	redis.save()

	if done == NUMQUES:
		clearRoom()



# This function send the clients the details of the first question
# Called only one "immediately" after the creation of the game
# This function is important to kick start the game
def sendFirstQuestionInfoToClient(room, usersInRoom):
	done = 0

	# Retrieve the details of the very first ques for the given room
	commonDataToSend = getNextQuestionForRoom(room, done)

	# There is no customized message for the first question
	# Hence broadcast across room can be used to send the details of the next question
	emit('nextQuestion', {'data': json.dumps(commonDataToSend)}, room = room)



# For a given room, retrieve and return the next question to be asked
# Also return array of answers, time and index along with the question in the dict
def getNextQuestionForRoom(room, done):
	# Handle situation when we have reached the last question
	# If this happens then we have to clear the room and record the game into the db
	if done == NUMQUES:
		return {}

	# When there are questions left in the game, retrieve the next game and send
	flashcardsJson = json.loads(redis.hget("ROOMS_CARDS", room))
	nextQues = flashcardsJson[done]['question']
	nextAns = flashcardsJson[done]['answers']
	commonDataToSend = {"question":nextQues, "answers":nextAns, "time": 10, "index": str(done+1)}

	return commonDataToSend