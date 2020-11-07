import socket
import json
import requests
from _thread import *
import threading
import time   
import random

match_lock = threading.Lock()
matches = {}

class Match:
	numMatches = 0;

def connectClientToServer(id, sock):
	print("D")

	server_address = ('localhost', 12345)

	messageBody = {}
	messageBody['connect'] = None
	messageBody['user_id'] = str(id)

	m = json.dumps(messageBody)
	sock.sendto(bytes(m,'utf8'), server_address)

	data, serverAddr = sock.recvfrom(1024)
	#print(data)
	data = json.loads(data)

	matchAddr = (serverAddr[0], data['matchSocket'][1])
	print(matchAddr)

	# Store match data
	# That way the clients have access to the same data
	match_lock.acquire()
	matches[data['matchId']] = data
	match_lock.release()

	#playMatch(id, data['matchId'], matchSock, sock)
	playMatch(id, data['matchId'], matchAddr, sock,)

	print(id)

def playMatch(userId, matchId, matchAddr, serverSock):
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

	print(" ")
	print(matches[matchId]['results'])

	match_lock.release()
	Match.numMatches+=1;

	m = json.dumps(matches[matchId])
	matchSock.sendto(bytes(m,'utf8'), matchAddr)

def main():
	for i in range(0, 6):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('localhost', 12345)
		sock.connect(server_address)

		start_new_thread(connectClientToServer, (i, sock, ))

	while True:
		time.sleep(1/30)

if __name__ == '__main__':
	main()
