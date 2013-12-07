#!/usr/bin/env python

import random
import time
import pickle
import socket
import sys
import cards_client
from cards_client import card, Player
from threading import Thread
from PyQt4 import QtGui, QtCore
import pdb

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.even = True
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('invalidIP'), self.invalid)
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('notify(PyQt_PyObject)'), self.notify)
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('Started'), self.expand)
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('Resize'), self.resizeEverything)
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('waiting(PyQt_PyObject)'), self.updateWaiting)
        
    def initUI(self):
    
        #Central Widget
        self.spreading = Cards()
        self.setCentralWidget(self.spreading)
        
        self.statusBar()
        
#        self.resize(650,400)
        self.center()
        self.setWindowTitle('Cards')
        self.show()
        
    def resizeEverything(self):
        self.resize(650,400)
        self.adjustSize()
        
    def expand(self):
        self.resize(650,400)
        self.setWindowTitle('Cards - Playing as {0}'.format(self.spreading.me.name))
        self.statusBar().showMessage("Connected!")
        self.spreading.wait()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def invalid(self):
        self.statusBar().showMessage("Invalid IP")
        
    def notify(self, message):
        self.statusBar().showMessage(message)
        
    def updateWaiting(self, name):
        self.statusBar().showMessage("Waiting for {0}{1}".format("others" if not name else name, "..." if self.even else ".."))
        self.even = not self.even
        
class Cards(QtGui.QWidget):
    
    def __init__(self):
        super(Cards, self).__init__()
        self.choice = None
        self.timer = QtCore.QTimer()
        self.initUI()
        
        
    def initUI(self):
        self.vbox = QtGui.QVBoxLayout()
        self.hbox = QtGui.QHBoxLayout()
        self.description = "Welcome to cards!"
        self.descriptionLabel = QtGui.QLabel(self.description)
        self.vbox.addWidget(self.descriptionLabel)
        self.grid = QtGui.QGridLayout()
        
        #Widgets
        self.word = QtGui.QLabel("Enter IP Address:")
        
        self.ipEdit = QtGui.QLineEdit()
        
        self.nameLabel = QtGui.QLabel("Enter name:")
        
        self.nameEdit = QtGui.QLineEdit()
        self.nameEdit.setText("Player")
        
        
        #Connections
        self.startButton = QtGui.QPushButton('Connect')
        self.startButton.setAutoDefault(True)
        self.startButton.setGeometry(100,100,100,100)
        self.startButton.clicked.connect(self.start)
        
        #Layout
        self.grid.addWidget(self.word,0, 0)
        self.grid.addWidget(self.ipEdit, 0, 1)
        self.grid.addWidget(self.nameLabel, 1, 0)
        self.grid.addWidget(self.nameEdit, 1, 1)
        self.grid.addWidget(self.startButton, 2, 1)
        
        self.hbox.addLayout(self.grid)
        self.scoresDisplay = QtGui.QTextEdit()
        self.scoresDisplay.hide()
        self.scoresDisplay.setReadOnly(True)
        self.scoresDisplay.setHtml("<h3>Scores</h3>")
        self.hbox.addWidget(self.scoresDisplay)
        
        self.vbox.addLayout(self.hbox)
        
#        vbox.addWidget(self.word)
#        vbox.addWidget(self.ipEdit)
#        vbox.addWidget(self.startButton)
        
        self.setLayout(self.vbox)
#        self.setLayout(self.grid)
        self.gridWidgets = [self.word,self.ipEdit,self.nameLabel,self.nameEdit,self.startButton]
        
    def start(self):
        print("start")
        try:
            print(self.ipEdit.text())
            self.me = cards_client.ClientPlayer(self.ipEdit.text(), 12345, str(self.nameEdit.text()) if self.nameEdit.text() != '' else "FNG")
            self.game = cards_client.Game(self.ipEdit.text(), 12345, self.me)
           
            for widget in self.gridWidgets:
                while not widget.isHidden():
                     t = GenericThread(widget.hide)
                     t.start()
                print("Hiding " + str(widget))
            QtGui.QApplication.processEvents()
            self.submitButton = QtGui.QPushButton('Submit')
            self.submitButton.setDisabled(True)
            self.submitButton.clicked.connect(self.submit)
            self.me.hand = [cards_client.card("entity","") for i in range(5)]
            self.guiHand = []
            self.guiPool = []
            self.scoresDisplay.show()
            self.judged = False
            self.updated = False
            
#            self.descriptionLabel.setFixedWidth(210)
            self.descriptionLabel.setWordWrap = True
            
#            self.grid.addWidget(self.descriptionLabel,0,2)
            
            self.grid.addWidget(self.submitButton,4,2)
            
            for card in self.me.hand:
                self.guiHand.append(QtGui.QPushButton(""))
            for i, card in enumerate(self.guiHand):
                card.setFixedSize(210,300)
                card.setCheckable = True
                card.clicked.connect(self.choose)
                self.grid.addWidget(card,1,i)
                    
            QtGui.qApp.emit(QtCore.SIGNAL("Started"))
        except Exception as e:
            print(e.args)
            QtGui.qApp.emit(QtCore.SIGNAL("invalidIP"))
            raise
            
    def submit(self):
        self.me.directSubmit(self.choice,self.me.isJudge)
        self.submitButton.setDisabled(True)
        self.judged = True
#        self.descriptionLabel.setText("The description for the round was: {0}.".format(self.description.strip('\n')))
        
    def choose(self, cardList=[]):
        if not self.guiHand[0].isEnabled():
            cardList = self.guiPool
        else:
            cardList = self.guiHand
            
        sender = self.sender()        
        self.choice = cardList.index(sender)
        for button in cardList:
            button.setChecked(False)
        sender.setDown(True)
        print(self.choice)
        
    def updateGuiHand(self):
        while len(self.me.hand) > len(self.guiHand):
            self.guiHand.append(QtGui.QPushButton(""))
        for i, card in enumerate(self.guiHand):
            card.setFixedSize(210,300)
            card.setCheckable = True
            card.clicked.connect(self.choose)
            self.grid.addWidget(card,1,i)
        for i,button in enumerate(self.guiHand):
            button.setText(self.me.hand[i].text)
            
    def updateGuiPool(self):
        for button in self.guiHand:
            button.setDisabled(True)
        while len(self.me.pool) > len(self.guiPool):
            self.guiPool.append(QtGui.QPushButton(""))
            print(self.guiPool)
        for i, card in enumerate(self.guiPool):
            card.setFixedSize(210,300)
            card.setCheckable = True
            card.clicked.connect(self.choose)
            self.grid.addWidget(card,2,i)
            card.show()
        self.submitButton.setDisabled(False)
        
#        time.sleep(30)
            
        for i,button in enumerate(self.guiPool):
            button.setText(self.me.pool[i].text)
            
    def cleanGuiPool(self):
        for button in self.guiPool:
            button.hide()
        for button in self.guiHand:
            button.setDisabled(False)
        self.adjustSize()
        QtGui.qApp.emit(QtCore.SIGNAL("Resize"))
            
    def wait(self):
        QtGui.QApplication.processEvents()
        
        if not self.updated:
            myTurn, slowPlayer = self.me.myTurn()
            if myTurn:
                self.me.updateTurnInfo()
                self.description = self.game.description
                self.descriptionLabel.setText("The description for this round is: {0}.".format(self.description.strip('\n')))
                QtGui.qApp.emit(QtCore.SIGNAL("notify(PyQt_PyObject)"), "Your turn!")
                self.choice = 0
                if self.me.isJudge:
                    QtGui.qApp.emit(QtCore.SIGNAL("notify(PyQt_PyObject)"), "Your turn! You are judging.")
    #                pdb.set_trace()
                    self.me.updatePool()
                    print(self.me.pool)
                    self.updateGuiPool()
                    self.updated = True
                else:
                    self.submitButton.setDisabled(False)
                    self.me.updateHand()
                    self.updateGuiHand()
                    self.updated = True
            else:
                QtGui.qApp.emit(QtCore.SIGNAL("waiting(PyQt_PyObject)"), slowPlayer)
        if self.judged:
            self.cleanGuiPool()
            self.timer.singleShot(1000,self.waitForRoundEnd)
        else:
            self.timer.singleShot(1000,self.wait)
        
    def waitForRoundEnd(self):
        self.judged = False
        self.updated = False
        QtGui.qApp.emit(QtCore.SIGNAL("waiting(PyQt_PyObject)"), "judgement")
        if self.game.roundEnd:
            winner, scores, pool = self.game.scores
            text = ("{0} won this round!".format(winner)) + '\n'
            for key in pool.keys():
                text += "{0} submitted '{1}'".format(pool[key],key.strip('\n'))
            print(text)
            self.timer.singleShot(1000,self.wait)
            self.updateScores(scores)
            helpBox = QtGui.QMessageBox()
            helpBox.about(self, "Submissions", QtCore.QString(text))
        else:
            self.timer.singleShot(500,self.waitForRoundEnd)
            
    def updateScores(self,scores):
        text = "<h3>Scores</h3><table>"
        for player in scores.keys():
            text += '''<tr>
            <td>{0}: </td>
            <td>{1}</td>'''.format(player,scores[player])
        text += "</table>"
        self.scoresDisplay.setHtml(text)
    def changeImg(self, label):
        label.setPixmap(self.cardSelectedImage)
        print("Changed image")
        
class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.function(*self.args,**self.kwargs)
        return
            
class CardLabel(QtGui.QLabel):
#    def __init__(self, text, number):
#        super(CardLabel, self).__init__(text)
#        self.number = number
    clicked = QtCore.pyqtSignal
    def mouseReleaseEvent(self,ev):
        self.emit(QtCore.SIGNAL('clicked(CardLabel)'), self)
#        self.clicked.emit()
       
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
