import socket
import json
import requests
from _thread import *
import threading
import time   
import random

match_lock = threading.Lock()
matches = {}
matchLogs = {}

playerIds = []

class Match:
	numMatches = 0;

def connectClientToServer(userId, sock):

	server_address = ('localhost', 12345)

	messageBody = {}
	messageBody['connect'] = None
	messageBody['user_id'] = str(userId)

	m = json.dumps(messageBody)
	sock.sendto(bytes(m,'utf8'), server_address)

	data, serverAddr = sock.recvfrom(1024)
	#print(data)
	data = json.loads(data)

	matchAddr = (serverAddr[0], data['matchSocket'][1])

	# Store match data
	# That way the clients have access to the same data
	match_lock.acquire()
	matches[data['matchId']] = data
	match_lock.release()

	#playMatch(id, data['matchId'], matchSock, sock)
	playMatch(userId, data['matchId'], matchAddr, sock,)

def playMatch(userId, matchId, matchAddr, serverSock):
	print(str(userId) + " Start Match")
	matchSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	matchSock.connect(matchAddr)

	match_lock.acquire()

	# First come first serve
	if (len(matches[matchId]['results']) == 0):
		players = matches[matchId]['players']

		# Pick a random winner id
		randWinner = players[random.randint(0, len(players)-1)]['user_id']

		print(randWinner + " wins")

		matches[matchId]['results'][randWinner] = 'win'

		# Everyone that isn't a winner is a loser
		for player in players:
			if (player['user_id'] != randWinner):
				matches[matchId]['results'][player['user_id']] = 'lose'

	match_lock.release()

	m = json.dumps(matches[matchId])
	matchSock.sendto(bytes(m,'utf8'), matchAddr)

	# Add result to log
	data = matchSock.recvfrom(1024)
	matchSock.close()

	print(str(userId) + " End Match")

	if matchId not in matchLogs.keys():
		Match.numMatches+=1;
		matchLogs[matchId] = data

	playerIds.append(userId)
	print(playerIds)

	while True:
		time.sleep(1/30)
	# for match in matchLogs.items():
	# 	print(" ")
	# 	print(match)

def main():
	for i in range(0, 10):
		playerIds.append(i)

	while Match.numMatches <= 10:
		if (len(playerIds) > 0):
			i = playerIds.pop()

			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			server_address = ('localhost', 12345)
			sock.connect(server_address)

			start_new_thread(connectClientToServer, (i, sock, ))

	for match in matchLogs.items():
		print(" ")
		print(match)

	time.sleep(1/30)

if __name__ == '__main__':
	main()
