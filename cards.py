#!/usr/bin/env python

import random

class player():
    def __init__(self, number):
        self.hand = []
        self.score = 0
        self.pool = []
        self.number = number
        self.dCard = None
        self.name = ""
        
    def __repr__(self):
        return "player({0})".format(self.number)
        
    def __str__(self):
        return self.name
        
    def __hash__(self):  #identity of player is determined by number, not name
        return self.number
        
    def __eq__(self,other):
        return (hash(self) == hash(other))
        
    def submit(self,targetPlayer):
        print("{0}'s turn to submit.".format(str(self)))
        self.displayCards(self.hand)
        choice = self.chooseCard(self.hand)  #pick a card from your hand
        targetPlayer.pool.append(self.hand.pop(choice))  #take it away and give it to the target player
        
    def displayCards(self,cards):
        for i, card in enumerate(cards):
            print("{0}. {1}".format(i+1, card))
            
    def judge(self):        
        print("{0} is now judging. Choose the card that best matches the description: {1}".format(str(self),str(self.dCard)))
        random.shuffle(self.pool)
        self.displayCards(self.pool)
        choice = self.chooseCard(self.pool)
        return self.pool[choice].owner
        
    def chooseCard(self,cards):
        while True:
            try:
                choice = int(raw_input("Enter card number: ")) - 1
                cards[choice]
                return choice
            except (ValueError,IndexError):
                print("Invalid entry.")
                continue
        
class deck():
    def __init__(self):
        self.descriptorCards = self.parseCards("test-adjs.txt","descriptor")
        self.entityCards = self.parseCards("test-nouns.txt","entity")
        
    def parseCards(self, path, cardType):
        f = open(path)
        cards = [card(cardType,word) for word in f.readlines()]
        f.close()               
        return cards
        
    def deal(self, targetPlayer):
        targetPlayer.hand.append(self.entityCards.pop())
        targetPlayer.hand[-1].setOwner(targetPlayer)
        
    def dealDCard(self, targetPlayer):
        targetPlayer.dCard = self.descriptorCards.pop()
        
    def shuffleCards(self):
        random.shuffle(self.descriptorCards)
        random.shuffle(self.entityCards)
        
class card():
    def __init__(self,cardType,text):
        self.cardType = cardType
        self.text = text
        self.owner = ""
        
    def __repr__(self):
        return repr(self.text)
        
    def __str__(self):
        return self.text
        
    def setOwner(self, player):
        self.owner = str(player)
        
class game():
    def __init__(self, Deck):
        numPlayers = int(raw_input("How many players?: "))
        self.players = [player(i) for i in range(numPlayers)]
        self.judge = random.choice(self.players)
        self.deck = Deck
        
    def getNames(self):
        for player in self.players:
            player.name = raw_input("Enter name for {0}: ".format(repr(player)))
    
    def drawCards(self):
        for player in self.players:
            while len(player.hand) < 5:  #deal cards till player has 5 cards
                self.deck.deal(player)
        
    def newRound(self):
        self.judge.pool = []  #reset judge's pool to empty
        self.judge.dCard = None
        self.judge = self.players[(self.players.index(self.judge) + 1)%len(self.players)]  #rotate judge position
        print(str(self.judge) + " is now the judge!")
        self.deck.dealDCard(self.judge)
        print("The description for this round is: {0}\n".format(self.judge.dCard))
        for player in self.players:
            if player != self.judge:
                player.submit(self.judge) #player submits a card
                self.deck.deal(player) #player draws a card after submission
                print("---")
        winnerName = self.judge.judge()  #judge judges
        for player in self.players:
            if winnerName == str(player):
                player.score += 1
                print("{0} won this round!".format(str(player)))
                break
                
    def endGame(self):
        print("\nScores: ")
        for player in self.players:
            print("{0}: {1}".format(str(player), player.score))
        
if __name__ == "__main__":
    Deck = deck()
    Deck.shuffleCards()
    Game = game(Deck)
    Game.getNames()
    Game.drawCards()
    print("Welcome to cards!\n")
    try:
        while True:
            Game.newRound()
            print("\n----------------\n----------------\n")
    except KeyboardInterrupt:
        Game.endGame()
    
    
