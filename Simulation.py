import socket
import json
import requests
from _thread import *
import threading
import time   

def connectClientToServer(id, sock):
		server_address = ('localhost', 12345)
	
		messageBody = {}
		messageBody['connect'] = None
		messageBody['user_id'] = str(id)

		m = json.dumps(messageBody)
		sock.sendto(bytes(m,'utf8'), server_address)

		data = sock.recvfrom(1024)
		print(str(data))

def main():
	for i in range(0, 5):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = ('localhost', 12345)
		sock.connect(server_address)

		start_new_thread(connectClientToServer, (i, sock, ))

	while True:
		time.sleep(1/30)

if __name__ == '__main__':
	main()
