import requests
import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

class Matches:
   numMatches = 0
   matches = []

playerTiers = {
   500: {'waitTime' : 0, 'players' : []}, 
   1000: {'waitTime' : 0, 'players' : []}, 
   1500: {'waitTime' : 0, 'players' : []}, 
   2000: {'waitTime' : 0, 'players' : []}, 
   2500: {'waitTime' : 0, 'players' : []}, 
   3000: {'waitTime' : 0, 'players' : []}
   } 

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = json.loads(data)

      user_profile = requestAPI(data['user_id'])

      user_profile['address'] = addr 
      assignLobbyRoom(user_profile)

      # if addr in clients:
      #    for params in data:
      #       if 'heartbeat' in params:
      #          clients[addr]['lastBeat'] = datetime.now()
           
      # else:
      #    for params in data:
      #       if 'connect' in params:
      #          # Fill in client information and add to dict
      #          clients[addr] = {}
      #          clients[addr]['lastBeat'] = datetime.now()

      #          # Initialize message to be sent to new player
      #          GameState = {"cmd": 1, "players": []}

      #          # C# Command class, Player class
      #          message = {"cmd": 0,"player":{"id":str(addr)}} #0 = new player connected
      #          message["cmd"] = 0
      #          message["player"] = {"id":str(addr)}

      #          m = json.dumps(message)
      #          for c in clients:
      #             sock.sendto(bytes(m,'utf8'), (c[0],c[1])) #0 = address, 1 = port
      #             # Create information about the other clients
      #             player = {}
      #             player['id'] = str(c) # (address, port)
      #             # Add information to message
      #             GameState['players'].append(player)

      #          # Send the new player the clients list
      #          new_client_m = json.dumps(GameState)
      #          sock.sendto(bytes(new_client_m, 'utf8'), addr)

def cleanClients(sock):
   while True:
      dropped_players = []
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:

            # Track dropped player
            player = {}
            player['id'] = str(c)
            dropped_players.append(player)

            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()

      # Message all connected clients about dropped clients
      if (len(dropped_players) > 0):
         message = {"cmd": 2, "players": dropped_players}
         m = json.dumps(message);
         for c in clients:
            sock.sendto(bytes(m, 'utf8'), (c[0], c[1]))
      
      time.sleep(5)

def assignLobbyRoom(user_profile):

   rankingScore = user_profile['score']

   # Sort connecting clients into rooms based on their rank score
   for tier in playerTiers.keys():
      if int(rankingScore) <= tier:

         playerTiers[tier]['players'].append(user_profile) # Add user to tier list
         
         if len(playerTiers[tier]['players']) == 1:
            playerTiers[tier]['waitTime'] = datetime.now()
         
         break

   # for tier in playerTiers.keys():
   #    print(playerTiers[tier])
   #    print("")

def assignMatchRoom(sock):
   for tier in playerTiers.keys():
      
      # There are more than 3 players waiting in the current tier
      if len(playerTiers[tier]['players']) >= 3:
         generateMatch(sock, tier, 3)

      # There are two players waiting in the current tier
      elif len(playerTiers[tier]['players']) == 2 and (datetime.now() - playerTiers[tier]['waitTime']).total_seconds() > 5:
         generateMatch(sock, tier, 2)

      #print(playerTiers[tier])
   for match in Matches.matches:
      print("")
      print(match)

def generateMatch(sock, tier, numPlayersInMatch):
   matchInfo = {"matchId" : Matches.numMatches, "players" : [], "results" : {}}
   Matches.numMatches+=1

   # Assign first numPlayersInMatch players from the tier to the match
   for i in range(0, numPlayersInMatch):
      matchInfo["players"].append(playerTiers[tier]['players'].pop(0))

    # Create a new socket for this match
   newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   newSock.bind(('',0))
   matchInfo["matchSocket"] = newSock.getsockname()

   Matches.matches.append(matchInfo)

   # Send match info to involved players
   for player in matchInfo["players"]:
      m = json.dumps(matchInfo)
      sock.sendto(bytes(m,'utf8'), player['address'])

   # Start new thread for the match
   start_new_thread(gameLoop, (newSock,))

def manageMatch(sock):
   data, addr = sock.recvfrom(1024)
   data = json.loads(data)

def gameLoop(sock):
   while True:

      # Assign clients to matches
      assignMatchRoom(sock)

      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)

      for c in clients:
         player = {}
         player['id'] = str(c)
         GameState['players'].append(player)
      
      s=json.dumps(GameState)
      print(s)
      
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      
      clients_lock.release()
      time.sleep(1/30)

def requestAPI(id):
   lambdaEndpoint = "https://z67un5qyea.execute-api.us-east-2.amazonaws.com/default/MatchMaking"
   requestBody = json.dumps({"user_id": str(id)})

   response = requests.get(lambdaEndpoint, data=requestBody)
   responseBody = json.loads(response.content)
   return responseBody

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1/30)

if __name__ == '__main__':
   main()
