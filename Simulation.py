import socket
import json
import requests
from _thread import *
import threading
import time   
import random
import sys

match_lock = threading.Lock()
matches = {}
matchLogs = {}

playerIds = []

class Match:
	numMatches = 0;

server_address = ('3.130.200.122', 12345)

def connectClientToServer(userId, sock):
	messageBody = {}
	messageBody['connect'] = None
	messageBody['user_id'] = str(userId)

	m = json.dumps(messageBody)
	sock.sendto(bytes(m,'utf8'), server_address)

	print(str(userId) + " connected to server")

	data, serverAddr = sock.recvfrom(1024)
	data = json.loads(data)

	matchPort = data['matchSocket'][1]
	print(matchPort)

	# Store match data
	# That way the clients have access to the same data
	match_lock.acquire()
	matches[data['matchId']] = data
	match_lock.release()

	playMatch(userId, data['matchId'], matchPort, sock,)

def playMatch(userId, matchId, matchPort, serverSock):
	print(str(userId) + " Start Match")
	matchSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	matchSock.connect((server_address[0], matchPort))
	print("match " + str(matchId) + " on socket " + str((server_address[0], matchPort)))

	match_lock.acquire()

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

		matches[matchId]['matchState'] = "End"

	#print(str(userId) + " End Match")
	match_lock.release()

	m = json.dumps(matches[matchId])
	matchSock.sendto(bytes(m,'utf8'), (server_address[0], matchPort))

	#time.sleep(5)
	print("Match finish")

	# Add result to log
	data = matchSock.recvfrom(1024)

	print(str(userId) + " End Match")

	# Since every player will have the same copy of results, use this to keep one copy
	if matchId not in matchLogs.keys():
		Match.numMatches+=1;
		matchLogs[matchId] = data

	playerIds.append(userId)

	while True:
		time.sleep(1/30)

def main(numSimulations):
	for i in range(0, 10):
		playerIds.append(i)

	while Match.numMatches < numSimulations:
		if (len(playerIds) > 0):
			i = playerIds.pop()

			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.connect(server_address)

			start_new_thread(connectClientToServer, (i, sock, ))

	f = open("matchResult.txt", "w")
	for match in matchLogs.items():
		f.write("\n")
		f.write("Match ID: " + str(match[0]))
		f.write("\n")

		for player in (json.loads((match[1])[0]))['players']:
			f.write(str(player))
			f.write("\n")

		f.write("\n")

		print("\n")
		print(match)

	f.close()

	time.sleep(1/30)

if __name__ == '__main__':
	try:
		main(int(sys.argv[1]))
	except:
		main(10)
