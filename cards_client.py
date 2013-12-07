#!/usr/bin/env python

import random
import time
import pickle
import socket
import sys
import ConfigParser

class ClientPlayer():
    def __init__(self,ip,port,name):
        self.hand = []  #Hand will hold card objects.
        self.score = 0
        self.pool = []  #When the player is the judge, other players submit to the player's pool
        self.number = int(time.time()*1000) % 1000000
        self.dCard = None  #When the player is judge, the player will have the descriptor card for the round
        self.name = name
        self.server = Requester(ip,port)
        self.otherPlayers = 0
        self.isJudge = False
        self.register()
        
    def __repr__(self):
        return "player({0})".format(self.number)
        
    def myTurn(self):
        try:
            answer = self.server.request_info((self.number,'myturn'))
#            print(answer)
            return answer
        except socket.error:
            print("socket error")
            return (False, None)
        except EOFError as e:
#            print("EOFError")
#            print(e.args)
            return (False, None)
    
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
        
    def directSubmit(self, choice, winner=False):
        if not winner:
            self.server.send_info((self.number,'submission',choice))
        else:
            self.server.send_info((self.number,'winner',choice))
        
    def updateTurnInfo(self):
        self.otherPlayers, self.isJudge = self.server.request_info((self.number,'turninfo'))
        
    def updateHand(self):
        self.hand = self.server.request_info((self.number,'hand'))
        
    def updatePool(self):
        self.pool = self.server.request_info((self.number,'pool'))
        
    def register(self):
        self.server.send_info((self.number,self.name))
        
    def disconnect(self):
        self.server.send_info((self.number,'disconnect'))
    
    def displayCards(self,cards):
        for i, card in enumerate(cards):
            print("{0}. {1}".format(i+1, card))
            
    def judge(self):  #placeholder method that returns the ID of the owner of the winning card
        self.displayCards(self.pool)
        choice = self.chooseCard(self.pool)
        self.server.send_info((self.number,'winner',choice))
        print("Submitted")
        
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
    def __init__(self,ip,port):
        self.HOST = ip
        self.PORT = port    #our port from before
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
#        data = cli.recv(self.BUFSIZE)
        
class Game():
    def __init__(self, ip, port, me):
#        self.description = ""
#        self.roundEnd = False
        self.server = Requester(ip, port)
        self.me = me
        
    @property
    def description(self):
        return self.server.request_info((self.me.number,'description'))
        
    @property
    def roundEnd(self):
#        print("Checking for round end")
        try:
            result = self.server.request_info((self.me.number,'roundEnd'))
#            print(result)
            return result
        except socket.error:
            return False
        
    @property
    def scores(self):
        return self.server.request_info((self.me.number,'scores'))
        
def update(s):
    sys.stdout.write("\r                             ")
    sys.stdout.flush() 
    sys.stdout.write("\r" + (s))
    sys.stdout.flush()

class ConfigReader():
    @staticmethod
    def getPort():
        Config = ConfigParser.ConfigParser()
        try:
            with open("settings.ini",'r') as cfgfile:
                Config.readfp(cfgfile)
                Config.sections()
                port = Config.getint('Settings', 'Port')
                cfgfile.close()
            return port
        except:
            print("Error getting settings, reverting to default.")
            Config = ConfigParser.ConfigParser()
            Config.add_section('Settings')
            Config.set('Settings','Port',2809)
            with open("settings.ini",'w') as cfgfile:
                Config.write(cfgfile)
                cfgfile.close()
            return 2809           
            
if __name__ == "__main__":
    serverIp = raw_input("Enter server IP address: ")
#    port = int(raw_input("Enter server port: "))
    port = ConfigReader.getPort()
    me = ClientPlayer(serverIp, port, raw_input("Enter name: "))
    game = Game(serverIp, port, me)
#    time.sleep(30)
    while True:
        try:
            myTurn, slowPlayer = me.myTurn()
            update("Waiting for {0}...".format(slowPlayer if slowPlayer else "others"))            
            if myTurn:
                print("Your turn!")            
                me.updateTurnInfo()
                if me.isJudge:
                    print("You are judging.")
                    print("The description for this round is: {0}.".format(game.description.strip('\n')))
                    me.updatePool()
                    me.judge()
                else:
                    print("Submit a card.")
                    print("The description for this round is: {0}.".format(game.description.strip('\n')))
                    me.updateHand()
                    me.submit()
                    
                while True:
                    update("Waiting for judgement...")
                    if game.roundEnd:
                        winner, scores, pool = game.scores
                        print("{0} won this round!".format(winner))
                        for key in pool.keys():
                            print("{0} submitted '{1}'".format(pool[key],key.strip('\n')))
                        print("==Scores==")
                        for key in scores.keys():
                            print("{0}: {1}".format(key,scores[key]))
                        print("\n----------------\n----------------\n")
                        break
                    time.sleep(0.5)
                    update("Waiting for judgement.. ")
                    time.sleep(0.5)
            time.sleep(0.5)
            update("Waiting for {0}.. ".format(slowPlayer if slowPlayer else "others"))
            time.sleep(0.5)
        except KeyboardInterrupt:
            me.disconnect()
            sys.exit(0)
        except socket.error:
            print("Connection lost.")
            time.sleep(5)
            continue
