#!/usr/bin/env python
#TODO:who are we waiting for?

import random
import socket
import pickle
import time
import ConfigParser
import sys

class SocketManager:

    def __init__(self, address):
        self.address = address


    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.address)
        return self.sock


    def __exit__(self, *ignore):
        self.sock.close()
        
class Player():
    def __init__(self, number, name):
        self.hand = []  #Hand will hold card objects.
        self.score = 0
        self.pool = []  #When the player is the judge, other players submit to the player's pool
        self.number = number
        self.dCard = None  #When the player is judge, the player will have the descriptor card for the round
        self.name = name
        
    def __repr__(self):
        return "player({0})".format(self.number)
        
    def __str__(self):
        return self.name
        
    def __hash__(self):  #Currently the hash is just their player number, but will change in the future.
        return self.number
        
    def __eq__(self,other):  #equality of two players is determined by comparing their hashes
        return (hash(self) == hash(other))
        
    def submit(self,targetPlayer,choice): #The submit method will eventually take input from other devices. The console is the placeholder input for now.
        print("{0}'s turn to submit.".format(str(self)))
        self.displayCards(self.hand)  #Player will want to look at their hand to decide. The GUI will display this in the future.
        targetPlayer.pool.append(self.hand.pop(choice))  #take it away and give it to the target player
        
    def displayCards(self,cards):
        for i, card in enumerate(cards):
            print("{0}. {1}".format(i+1, card))
            
    def judge(self,choice):  #placeholder method that returns the ID of the owner of the winning card
        print("{0} is now judging. Choose the card that best matches the description: {1}".format(str(self),str(self.dCard)))
        self.displayCards(self.pool)
        try:
            return self.pool[choice].owner
        except IndexError:
            print("Only one or players left in the game, server shutting down.")
            sys.exit(0)
        
    def chooseCard(self,cards):  #Once again, this method is a placeholder. Future versions will involve picking thru a GUI.
        while True:
            try:
                choice = int(raw_input("Enter card number: ")) - 1
                cards[choice]  #Test to see they've entered a number in range
                return choice
            except (ValueError,IndexError):  #If what they've entered is in any way invalid, continue
                print("Invalid entry.")
                continue
        
class deck():
    def __init__(self,desc="test-adjs.txt",ent="test-nounds.txt"):
        self.descriptorCards = self.parseCards(desc,"descriptor")  #The two decks of cards are parsed from text files
        self.entityCards = self.parseCards(ent,"entity")
        
    def parseCards(self, path, cardType): #Parser assumes each line is its own card and returns a list of card objects
        f = open(path)
        cards = [card(cardType,word) for word in f.readlines()] 
        f.close()               
        return cards
        
    def deal(self, targetPlayer): #Pops a single card off the entity cards pile and gives it to the target player
        targetPlayer.hand.append(self.entityCards.pop())
        targetPlayer.hand[-1].owner = targetPlayer
        
    def dealDCard(self, targetPlayer):  #Pops a single card off the descriptor cards pile and gives it to the target player
        targetPlayer.dCard = self.descriptorCards.pop()
        
    def shuffleCards(self):
        random.shuffle(self.descriptorCards)
        random.shuffle(self.entityCards)
        
class card():
    def __init__(self,cardType,text):
        self.cardType = cardType  #Whether the card is an entity or descriptor. At the moment this isn't really used.
        self.text = text  #The text of the card
        self.owner = None  #The hash of the owner of the card. Used to identify whose card the judge picked.
        
    def __repr__(self):
        return repr(self.text)
        
    def __str__(self):
        return self.text
    
    @property
    def owner(self):
        return self.__owner
        
    @owner.setter
    def owner(self, player):
        self.owner = hash(player)
        
class game():
    def __init__(self, Deck):
        self.numPlayers = int(raw_input("How many players?: "))
#        self.players = [player(i) for i in range(numPlayers)] #Creates a list of numPlayers player objects, each initialized to a unique id
        self.players = []
        self.deck = Deck
        config = ConfigReader()
        HOST = ''    #we are the host
#        PORT = int(raw_input("Port: "))    #arbitrary port not currently in use
        PORT = config.port
        ADDR = (HOST,PORT)    #we need a tuple for the address
        self.BUFSIZE = 4096    #reasonably sized buffer for data

                ## now we create a new socket object (serv)
                ## see the python docs for more information on the socket types/flags
        self.serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    

                ##bind our socket to the address
        self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv.bind((ADDR))    #the double parens are to create a tuple with one element
        self.initPlayers(self.numPlayers)
        print [player.name for player in self.players]
        self.judge = random.choice(self.players)
        self.winnerName = "Nobody"
        self.playersToRemove = []
        self.playersToAdd = []
        
    def initPlayers(self,numPlayers):
        while len(self.players) != numPlayers:
            self.serv.listen(5)    #5 is the maximum number of queued connections we'll allow
            print 'listening...'
            conn,addr = self.serv.accept()
            data = pickle.loads(conn.recv(self.BUFSIZE))
            print(data)
            newPlayer = Player(*data)
            if not any([newPlayer == player for player in self.players]):
                self.players.append(newPlayer)
            if str(data[1]) == 'myturn':
                conn.send(pickle.dumps((False,None)))
                conn.close()
        print(self.players)
    
    def drawCards(self):
        for player in self.players:
            while len(player.hand) < 5:  #deal cards till player has 5 cards
                self.deck.deal(player)
                
    def handleRequests(self,player):
        while True:
            self.serv.listen(5)    #5 is the maximum number of queued connections we'll allow
            print 'listening...'
            conn,addr = self.serv.accept()
            data = pickle.loads(conn.recv(self.BUFSIZE))
            print(data)
            if not any([data[0] == hash(person) for person in self.players]) and not any([data[0] == hash(person) for person in self.playersToAdd]):
                self.playersToAdd.append(Player(*data))
                print("Added {0}".format(data[0]))
            if str(data[1]) == 'myturn':
                conn.send(pickle.dumps((hash(player) == data[0],player.name)))
                conn.close()
            elif str(data[1]) == 'roundEnd':
                conn.send(pickle.dumps(self.roundEnd))
                conn.close()
            elif str(data[1]) == 'turninfo':
                conn.send(pickle.dumps((self.numPlayers,hash(self.judge) == data[0]))) #Sends number of other players and whether player is judge
                conn.close()
            elif data[1] == 'hand':
                conn.send(pickle.dumps(player.hand))
                conn.close()
            elif data[1] == 'description':
                conn.send(pickle.dumps(self.judge.dCard.text))
                conn.close()
            elif str(data[1]) == 'submission':
                player.submit(self.judge,data[2])
                self.deck.deal(player) #player draws a card after submission
                conn.close()
                print("---")
                return
            elif data[1] == 'pool':
                conn.send(pickle.dumps(self.judge.pool))
                conn.close()
            elif data[1] == 'scores':
                conn.send(pickle.dumps((self.winnerName,self.constructScoresDict(),self.constructPoolDict())))
                conn.close()
                return
            elif data[1] == 'disconnect':
                if not any([data[0] == hash(candidate) for candidate in self.playersToAdd]):
                    shouldReturn = False
                    for person in self.players:
                        shouldReturn = (person == player)
                        if data[0] == hash(person):
                            if person == self.judge:
                                self.judge = Player(-1,"Ghost")
                                self.judge.pool = person.pool
                                self.judge.dCard = person.dCard
                            print("{0} has disconnected!".format(person))
                            if self.players.index(person) > self.players.index(player):
                                self.players.remove(person)
                            else:
                                self.playersToRemove.append(person)
                    conn.close()
                    if shouldReturn:
                        return
                else:
                    for candidate in self.playersToAdd:
                        if data[0] == hash(candidate):
                            self.playersToAdd.remove(candidate)
                
            elif str(data[1]) == 'winner':
                winnerHash = self.judge.judge(data[2])
                conn.close()
                self.winnerName = "Nobody"
                self.findWinner(winnerHash)
                return
                
            if self.roundEnd:
                break
                
    def findWinner(self, winnerHash):
        for player in self.players:
            if winnerHash == hash(player):
                player.score += 1
                self.winnerName = player.name
                print("{0} won this round!".format(self.winnerName))
                return
               
    def newRound(self):
        self.judge.pool = []  #reset judge's pool to empty
        self.judge.dCard = None
        self.roundEnd = False
        self.winnerName = "Nobody"
        self.playersToRemove = []
        self.playersToAdd = []
        print [player.name for player in self.players]
        try:
            self.judge = self.players[(self.players.index(self.judge) + 1)%len(self.players)]  #rotate judge position
        except ValueError:
            self.judge = random.choice(self.players)
        print(str(self.judge) + " is now the judge!")
        self.deck.dealDCard(self.judge)
        print("The description for this round is: {0}\n".format(self.judge.dCard))
        for player in self.players:
            if player != self.judge:
                self.handleRequests(player)
            
        #Judging time
        random.shuffle(self.judge.pool)
        if self.judge.number != -1:
            self.handleRequests(self.judge)
        else:
            winnerHash = self.judge.judge(0)
            self.findWinner(winnerHash)
        
        #Clean up the round and send everyone useful info!
        start = int(time.time())
        self.roundEnd = True
        while int(time.time()) - start != 3:
            self.handleRequests(Player(1,"stragglers"))
        for player in self.playersToRemove:
        
            self.players.remove(player)
                
        self.players += self.playersToAdd
        self.drawCards()
        
    def constructScoresDict(self):
        result = {}
        for player in self.players:
            result[player.name] = player.score
        return result
        
    def constructPoolDict(self):
        result = {}
        playerIdDict = {player.number:player.name for player in self.players}
        for card in self.judge.pool:
            try:
                result[card.text] = playerIdDict[card.owner]
            except KeyError:
                pass
#        print(result)
        return result
            
    def endGame(self):
        print("\nScores: ")
        for player in self.players:
            print("{0}: {1}".format(str(player), player.score))
            
class ConfigReader():
    def __init__(self):
        self.port = 2809
        self.desc = "test-adjs.txt"
        self.ent = "test-nouns.txt"
        try:        
            self.initSettings()
        except:
            print("Error accessing settings.ini")
        
    def initSettings(self):
        Config = ConfigParser.ConfigParser()
        try:
            with open("settings.ini",'r') as cfgfile:
                Config.readfp(cfgfile)
                Config.sections()
                self.port = Config.getint('Settings', 'Port')
                self.desc = Config.get('Settings', 'Descriptors')
                self.ent = Config.get('Settings', 'Entities')
                cfgfile.close()
        except Exception as e:            
            print("Error getting settings, reverting to default.")
            Config = ConfigParser.ConfigParser()
            Config.add_section('Settings')
            Config.set('Settings','Port',2809)
            Config.set('Settings','Descriptors',"test-adjs.txt")
            Config.set('Settings','Entities',"test-nouns.txt")
            with open("settings.ini",'w') as cfgfile:
                Config.write(cfgfile)
                cfgfile.close()
            print(type(e))
            print(e.args)
            raise
                        
if __name__ == "__main__":
    config = ConfigReader()
    Deck = deck(config.desc,config.ent)   #Begin by initializing a deck
    Deck.shuffleCards()  
    Game = game(Deck)   #Initialize the game with the current deck
    Game.drawCards()  #Have players draw all the cards
    print("Welcome to cards!\n")
    try:
        while True:
            Game.newRound()
            print("\n----------------\n----------------\n")
    except KeyboardInterrupt:
        Game.endGame()
    
    
