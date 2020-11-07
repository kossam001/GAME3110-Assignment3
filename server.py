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
   matches = {}

playerTiers = {
   500: {'waitTime' : 0, 'players' : []}, 
   1000: {'waitTime' : 0, 'players' : []}, 
   1500: {'waitTime' : 0, 'players' : []}
   } 

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = json.loads(data)

      user_profile = requestAPI(data['user_id'])

      user_profile['address'] = addr 
      assignLobbyRoom(user_profile)

def cleanClients(sock):
   while True:
      dropped_players = []
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 10:

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
      if int(rankingScore) <= tier or tier == 1500:

         playerTiers[tier]['players'].append(user_profile) # Add user to tier list
         
         if len(playerTiers[tier]['players']) == 1:
            playerTiers[tier]['waitTime'] = datetime.now()
         
         break

def assignMatchRoom(sock):
   for tier in playerTiers.keys():
      
      # There are more than 3 players waiting in the current tier
      if len(playerTiers[tier]['players']) >= 3:
         generateMatch(sock, tier, 3)

      # There are two players waiting in the current tier
      elif len(playerTiers[tier]['players']) == 2 and (datetime.now() - playerTiers[tier]['waitTime']).total_seconds() > 5:
         generateMatch(sock, tier, 2)

def generateMatch(sock, tier, numPlayersInMatch):
   matchId = Matches.numMatches
   matchInfo = {"matchId" : matchId, "players" : [], "results" : {}, "startTime" : str(datetime.now())}
   Matches.numMatches+=1

   # Assign first numPlayersInMatch players from the tier to the match
   for i in range(0, numPlayersInMatch):
      matchInfo["players"].append(playerTiers[tier]['players'].pop(0))

    # Create a new socket for this match
   newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   newSock.bind(('',0))
   matchInfo["matchSocket"] = newSock.getsockname()

   Matches.matches[matchId] = matchInfo

   # Send match info to involved players
   for player in matchInfo["players"]:
      m = json.dumps(matchInfo)
      sock.sendto(bytes(m,'utf8'), player['address'])

   # Start new thread for the match
   start_new_thread(manageMatch, (newSock, matchId,))

def manageMatch(sock, matchId):
   matchMsgList = {}
   playersInMatch = Matches.matches[matchId]["players"]
   start_new_thread(matchConnectionLoop,(matchMsgList,sock,))

   # Match loop
   while len(playersInMatch) > 0:
      
      
      # Get all icoming 
      # while (len(matchEndMsgList) < len(playersInMatch)):
      #    data, addr = sock.recvfrom(1024)

      #    matchEndMsgList.append(addr)

      if len(matchMsgList) > 0:
         lambdaEndpoint = "https://ohe5ppwqv2.execute-api.us-east-2.amazonaws.com/default/UpdatePlayerScore"
         #requestBody = json.dumps({"user_id": str(id)})
         print(matchMsgList[list(matchMsgList.keys())[0]])

         response = requests.get(lambdaEndpoint, data=matchMsgList[list(matchMsgList.keys())[0]])
         responseBody = json.loads(response.content)
         responseBody = json.dumps(responseBody)

         for addr in matchMsgList:
            #print(response.content)
            sock.sendto(bytes(responseBody, 'utf8'), addr)

            # Match end - close socket as soon as all players notified
            playersInMatch = Matches.matches[matchId]["players"]
            playersInMatch.pop()

   time.sleep(1)
   sock.close()

def matchConnectionLoop(msgList, sock):
   while True:
      try:
         data, addr = sock.recvfrom(1024)
         msgList[addr] = data
      except:
         print("Match Over")
         break;

def gameLoop(sock):
   while True:

      # Assign clients to matches
      assignMatchRoom(sock)

      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      #print (clients)

      for c in clients:
         player = {}
         player['id'] = str(c)
         GameState['players'].append(player)
      
      s=json.dumps(GameState)
      #print(s)
      
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
