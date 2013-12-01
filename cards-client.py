#!/usr/bin/env python

#An outline of an engine for concept-to-description/category matching card game.

import random
import time
import pickle
import socket
import sys

class ClientPlayer():
    def __init__(self,ip):
        self.hand = []  #Hand will hold card objects.
        self.score = 0
        self.pool = []  #When the player is the judge, other players submit to the player's pool
        self.number = int(time.time()*1000)
        self.dCard = None  #When the player is judge, the player will have the descriptor card for the round
        self.name = raw_input("Enter name: ")
        self.server = Requester(ip)
        self.otherPlayers = 0
        self.isJudge = False
        self.register()
        
    def __repr__(self):
        return "player({0})".format(self.number)
        
    def myTurn(self):
        try:
            answer = self.server.request_info((self.number,'myturn'))
            return answer
        except socket.error:
            return False
        except EOFError:
            return False
    
    def __str__(self):
        return self.name
        
    def __hash__(self):  #Currently the hash is just their player number, but will change in the future.
        return self.number
        
    def __eq__(self,other):  #equality of two players is determined by comparing their hashes
        return (hash(self) == hash(other))
        
    def submit(self): #The submit method will eventually take input from other devices. The console is the placeholder input for now.
        print("{0}'s turn to submit.".format(str(self)))
        self.displayCards(self.hand)  #Player will want to look at their hand to decide. The GUI will display this in the future.
        choice = self.chooseCard(self.hand)  #pick a card from your hand
        self.server.send_info((self.number,'submission',choice))
        
    def updateTurnInfo(self):
        self.otherPlayers, self.isJudge = self.server.request_info((self.number,'turninfo'))
        
    def updateHand(self):
        self.hand = self.server.request_info((self.number,'hand'))
        
    def updatePool(self):
        self.pool = self.server.request_info((self.number,'pool'))
        
    def register(self):
        self.server.send_info((self.number,self.name))
    
    def displayCards(self,cards):
        for i, card in enumerate(cards):
            print("{0}. {1}".format(i+1, card))
            
    def judge(self):  #placeholder method that returns the ID of the owner of the winning card
        self.displayCards(self.pool)
        choice = self.chooseCard(self.pool)
        self.server.send_info((self.number,'winner',choice))
        
    def chooseCard(self,cards):  #Once again, this method is a placeholder. Future versions will involve picking thru a GUI.
        while True:
            try:
                choice = int(raw_input("Enter card number: ")) - 1
                cards[choice]  #Test to see they've entered a number in range
                return choice
            except (ValueError,IndexError):  #If what they've entered is in any way invalid, continue
                print("Invalid entry.")
                continue
class Player(ClientPlayer):
    pass       
class card():
    def __init__(self,cardType,text):
        self.cardType = cardType  #Whether the card is an entity or descriptor. At the moment this isn't really used.
        self.text = text  #The text of the card
        self.owner = None  #The hash of the owner of the card. Used to identify whose card the judge picked.
        
    def __repr__(self):
        return repr(self.text)
        
    def __str__(self):
        return self.text
        
    def setOwner(self, player):
        self.owner = hash(player)

class Requester():
    def __init__(self,ip):
        self.HOST = ip
        self.PORT = 12345    #our port from before
        self.ADDR = (self.HOST,self.PORT)
        self.BUFSIZE = 4096
        
    def request_info(self,request):
        cli = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        cli.connect((self.ADDR))
        info = pickle.dumps(request)
        cli.send(info)
        data = cli.recv(self.BUFSIZE)
#        print("Got a reply")
        return pickle.loads(data)
        
    def send_info(self,request):
        cli = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        cli.connect((self.ADDR))
        info = pickle.dumps(request)
        cli.send(info)
        data = cli.recv(self.BUFSIZE)
        
class Game():
    def __init__(self, ip):
#        self.description = ""
#        self.roundEnd = False
        self.server = Requester(ip)
        
    @property
    def description(self):
        return self.server.request_info((me.number,'description'))
        
    @property
    def roundEnd(self):
#        print("Checking for round end")
        try:
            result = self.server.request_info((me.number,'roundEnd'))
#            print(result)
            return result
        except socket.error:
            return False
        
    @property
    def scores(self):
        return self.server.request_info((me.number,'scores'))
        
def update(s):
    sys.stdout.write("\r" + (s))
    sys.stdout.flush()        
        
if __name__ == "__main__":
    serverIp = raw_input("Enter server IP address: ")
    me = ClientPlayer(serverIp)
    game = Game(serverIp)
#    time.sleep(30)
    while True:
        try:
            update("Waiting for others...")
            if me.myTurn():
                print("Your turn!")            
                me.updateTurnInfo()
                if me.isJudge:
                    print("You are judging.")
                    print("The description for this round is {0}.".format(game.description))
                    me.updatePool()
                    me.judge()
                else:
                    print("Submit a card.")
                    print("The description for this round is {0}.".format(game.description))
                    me.updateHand()
                    me.submit()
                    
                while True:
                    if game.roundEnd:
                        winner, scores = game.scores
                        print("{0} won this round!".format(winner))
                        print("==Scores==")
                        for key in scores.keys():
                            print("{0}: {1}".format(key,scores[key]))
                        print("\n----------------\n----------------\n")
                        break
                        
                    time.sleep(1)
            time.sleep(0.5)
            update("Waiting for others.. ")
            time.sleep(0.5)
        except KeyboardInterrupt:
            sys.exit(0)
        except socket.error:
            print("Connection lost.")
            time.sleep(5)
            continue
