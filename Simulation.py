import socket
import json
import requests

# def sendConnectMessage(id):



# try:
    
#     message = 'This is the message.  It will be repeated.'
#     m = json.dumps(message)
#     sock.sendall(bytes(m,'utf8'))
#     sock.sendto(bytes(m,'utf8'), ('localhost', 12345))

#     # Look for the response
#     amount_received = 0
#     amount_expected = len(message)

# finally:
#     print >>sys.stderr, 'closing socket'
    

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ('localhost', 12345)
	sock.connect(server_address)

	messageBody = {}
	messageBody['connect'] = None
	messageBody['user_id'] = '5'

	m = json.dumps(messageBody)
	sock.sendto(bytes(m,'utf8'), ('localhost', 12345))

	data = sock.recvfrom(1024)
	#responseBody = json.loads(response.content)
	print(str(data))
	sock.close()

if __name__ == '__main__':
   main()
   #sendConnectMessage('5')
