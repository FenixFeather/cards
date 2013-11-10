#!/usr/bin/env python

#An outline of an engine for concept-to-description/category matching card game.

import random
import datetime
import logging
import os
import random
from django.utils import simplejson
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class player():
    def __init__(self, number):
        self.hand = []  #Hand will hold card objects.
        self.score = 0
        self.pool = []  #When the player is the judge, other players submit to the player's pool
        self.number = number
        self.dCard = None  #When the player is judge, the player will have the descriptor card for the round
        self.name = ""  #Player's name is obtained thru game.getNames()
        
    def __repr__(self):
        return "player({0})".format(self.number)
        
    def __str__(self):
        return self.name
        
    def __hash__(self):  #Currently the hash is just their player number, but will change in the future.
        return self.number
        
    def __eq__(self,other):  #equality of two players is determined by comparing their hashes
        return (hash(self) == hash(other))
        
    def submit(self,targetPlayer): #The submit method will eventually take input from other devices. The console is the placeholder input for now.
        print("{0}'s turn to submit.".format(str(self)))
        self.displayCards(self.hand)  #Player will want to look at their hand to decide. The GUI will display this in the future.
        choice = self.chooseCard(self.hand)  #pick a card from your hand
        targetPlayer.pool.append(self.hand.pop(choice))  #take it away and give it to the target player
        
    def displayCards(self,cards):
        for i, card in enumerate(cards):
            print("{0}. {1}".format(i+1, card))
            
    def judge(self):  #placeholder method that returns the ID of the owner of the winning card
        print("{0} is now judging. Choose the card that best matches the description: {1}".format(str(self),str(self.dCard)))
        random.shuffle(self.pool)
        self.displayCards(self.pool)
        choice = self.chooseCard(self.pool)
        return self.pool[choice].owner
        
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
    def __init__(self):
        self.descriptorCards = self.parseCards("test-adjs.txt","descriptor")  #The two decks of cards are parsed from text files
        self.entityCards = self.parseCards("test-nouns.txt","entity")
        
    def parseCards(self, path, cardType): #Parser assumes each line is its own card and returns a list of card objects
        f = open(path)
        cards = [card(cardType,word) for word in f.readlines()] 
        f.close()               
        return cards
        
    def deal(self, targetPlayer): #Pops a single card off the entity cards pile and gives it to the target player
        targetPlayer.hand.append(self.entityCards.pop())
        targetPlayer.hand[-1].setOwner(targetPlayer)
        
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
        
    def setOwner(self, player):
        self.owner = hash(player)
        
class game():
    def __init__(self, Deck):
        numPlayers = int(raw_input("How many players?: "))
        self.players = [player(i) for i in range(numPlayers)] #Creates a list of numPlayers player objects, each initialized to a unique id
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
        winnerHash = self.judge.judge()  #call the judge method. This returns the hash of the winning player.
        for player in self.players:
            if winnerHash == hash(player):
                player.score += 1
                print("{0} won this round!".format(str(player)))
                break
                
    def endGame(self):
        print("\nScores: ")
        for player in self.players:
            print("{0}: {1}".format(str(player), player.score))
        
if __name__ == "__main__":
    Deck = deck()   #Begin by initializing a deck
    Deck.shuffleCards()  
    Game = game(Deck)   #Initialize the game with the current deck
    Game.getNames()   #Get player names
    Game.drawCards()  #Have players draw all the cards
    print("Welcome to cards!\n")
    try:
        while True:
            Game.newRound()
            print("\n----------------\n----------------\n")
    except KeyboardInterrupt:
        Game.endGame()
    
    
