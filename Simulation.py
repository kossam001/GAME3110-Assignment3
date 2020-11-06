import socket
import json
import requests
from _thread import *
import threading
import time   

matches = {}

def connectClientToServer(id, sock):
	print("D")

	server_address = ('localhost', 12345)

	messageBody = {}
	messageBody['connect'] = None
	messageBody['user_id'] = str(id)

	m = json.dumps(messageBody)
	sock.sendto(bytes(m,'utf8'), server_address)

	data, matchAddr = sock.recvfrom(1024)
	data = json.loads(data)

	print(data)

	# Store match data
	# That way the clients have access to the same data
	#match_lock.acquire()
	matches[data['matchId']] = data
	#match_lock.release()

	#print(matches)

	#playMatch(id, data['matchId'], matchSock, sock)
	start_new_thread(playMatch, (id, data['matchId'], matchAddr, sock,))

	print("C")

def playMatch(userId, matchId, matchAddr, serverSock):
	matchSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	matchSock.connect(matchAddr)

	print(" ")
	#print(matches)

	#match_lock.acquire()

	# First come first serve
	if (len(matches[matchId]['results']) == 0):
		matches[matchId]['results'][userId] = 'win'
	else:
		matches[matchId]['results'][userId] = 'lose'

	#match_lock.release()

	print(" ")
	print(matches)

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
