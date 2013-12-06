#!/usr/bin/env python

import random
import time
import pickle
import socket
import sys
import cards_client
from threading import Thread
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.even = True
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('invalidIP'), self.invalid)
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('notify'), self.notify)
        QtCore.QObject.connect(QtGui.qApp, QtCore.SIGNAL('Started'), self.expand)
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
        self.grid = QtGui.QGridLayout()
        vbox = QtGui.QVBoxLayout()
        
        #Widgets
        self.word = QtGui.QLabel("Enter IP Address:")
        
        self.ipEdit = QtGui.QLineEdit()
        
        self.nameLabel = QtGui.QLabel("Enter name:")
        
        self.nameEdit = QtGui.QLineEdit()
        self.nameEdit.setText("Player")
        
        
        #Connections
        self.startButton = QtGui.QPushButton('Start')
        self.startButton.setGeometry(100,100,100,100)
        self.startButton.clicked.connect(self.start)
        
        #Layout
        self.grid.addWidget(self.word,0, 0)
        self.grid.addWidget(self.ipEdit, 0, 1)
        self.grid.addWidget(self.nameLabel, 1, 0)
        self.grid.addWidget(self.nameEdit, 1, 1)
        self.grid.addWidget(self.startButton, 2, 1)
        
#        vbox.addWidget(self.word)
#        vbox.addWidget(self.ipEdit)
#        vbox.addWidget(self.startButton)
        
#        self.setLayout(vbox)
        self.setLayout(self.grid)
        self.gridWidgets = [self.word,self.ipEdit,self.nameLabel,self.nameEdit,self.startButton]
        
    def start(self):
        print("start")
        try:
            print(self.ipEdit.text())
            self.me = cards_client.ClientPlayer(self.ipEdit.text(), 12345, str(self.nameEdit.text()) if self.nameEdit.text() != '' else "FNG")
            self.game = cards_client.Game(self.ipEdit.text, 12345)
           
            for widget in self.gridWidgets:
                while not widget.isHidden():
                     t = GenericThread(widget.hide)
                     t.start()
#                    widget.hide()
                print("Hiding " + str(widget))
            QtGui.QApplication.processEvents()
            self.submitButton = QtGui.QPushButton('Submit')
            self.submitButton.setDisabled(True)
            self.submitButton.clicked.connect(self.submit)
            self.me.hand = [cards_client.card("entity","") for i in range(5)]
#            self.guiHand = {}
            self.guiHand = []
            self.descriptionLabel = QtGui.QLabel("")
            self.grid.addWidget(self.descriptionLabel,0,2)
#            self.cardImage = QtGui.QPixmap(('img/card.png')).scaled(210,300, QtCore.Qt.KeepAspectRatio)
#            self.cardSelectedImage = QtGui.QPixmap(('img/cardSelected.png')).scaled(210,300, QtCore.Qt.KeepAspectRatio)
            for card in self.me.hand:
                self.guiHand.append(QtGui.QPushButton(""))
#                self.guiHand.append(CardLabel("f"))
#                self.guiHand[CardLabel("f")] = i
#                for label in self.guiHand.keys():
#                    label.setPixmap(self.cardImage)
##                    label.clicked.connect(lambda: self.changeImg(label))
#                    QtCore.QObject.connect(label, QtCore.SIGNAL('clicked()'), self.changeImg)
#                    self.grid.addWidget(label,1,self.guiHand[label])
            self.grid.addWidget(self.submitButton,2,2)
#                self.guiHand[QtGui.QPushButton("")] = i
#                for card in self.guiHand.keys():
#                card.setFixedSize(210,300)
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
        self.me.directSubmit(self.choice)
        
    def choose(self):
        sender = self.sender()        
        self.choice = self.guiHand.index(sender)
        for button in self.guiHand:
            button.setChecked(False)
        sender.setDown(True)
        print(self.guiHand.index(sender))
        
    def updateGuiHand(self):
        
            
    def wait(self):
        QtGui.QApplication.processEvents()
        myTurn, slowPlayer = self.me.myTurn()
        if myTurn:
            QtGui.qApp.emit(QtCore.SIGNAL("notify(PyQt_PyObject)"), "Your turn!")
            self.submitButton.setDisabled(False)            
        else:
            QtGui.qApp.emit(QtCore.SIGNAL("waiting(PyQt_PyObject)"), slowPlayer)
#            print("Signaled")
        self.timer.singleShot(1000,self.wait)
            
#    def waitR(self):
#        while True:
#            myTurn, slowPlayer = self.me.myTurn()
#            if myTurn:
#                QtGui.qApp.emit(QtCore.SIGNAL("myturn"))
#            else:
#                QtGui.qApp.emit(QtCore.SIGNAL("waiting(string)"), slowPlayer)
#            time.sleep(1)
            
#    def wait(self):
#        self.workThread = WorkThread(self.me)
#        self.workThread.start()
            
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

class WorkThread(QtCore.QThread):
    def __init__(self, me):
        QtCore.QThread.__init__(self)
        self.me = me

    def run(self):
        while True:
            myTurn, slowPlayer = self.me.myTurn()
            if myTurn:
                QtGui.qApp.emit(QtCore.SIGNAL("myturn"))
            else:
                QtGui.qApp.emit(QtCore.SIGNAL("waiting(PyQt_PyObject)"), slowPlayer)
            print("hi")
            time.sleep(1)

            
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
    
#    serverIp = raw_input("Enter server IP address: ")
#    port = int(raw_input("Enter server port: "))
#    me = ClientPlayer(serverIp, port)
#    game = Game(serverIp, port)
##    time.sleep(30)
#    while True:
#        try:
#            myTurn, slowPlayer = me.myTurn()
#            update("Waiting for {0}...".format(slowPlayer))            
#            if myTurn:
#                print("Your turn!")            
#                me.updateTurnInfo()
#                if me.isJudge:
#                    print("You are judging.")
#                    print("The description for this round is {0}.".format(game.description.strip('\n')))
#                    me.updatePool()
#                    me.judge()
#                else:
#                    print("Submit a card.")
#                    print("The description for this round is {0}.".format(game.description.strip('\n')))
#                    me.updateHand()
#                    me.submit()
#                    
#                while True:
#                    update("Waiting for judgement...")
#                    if game.roundEnd:
#                        winner, scores, pool = game.scores
#                        print("{0} won this round!".format(winner))
#                        for key in pool.keys():
#                            print("{0} submitted '{1}'".format(pool[key],key))
#                        print("==Scores==")
#                        for key in scores.keys():
#                            print("{0}: {1}".format(key,scores[key]))
#                        print("\n----------------\n----------------\n")
#                        break
#                    time.sleep(0.5)
#                    update("Waiting for judgement.. ")    
#                    time.sleep(0.5)
#            time.sleep(0.5)
#            update("Waiting for {0}.. ".format(slowPlayer))
#            time.sleep(0.5)
#        except KeyboardInterrupt:
#            sys.exit(0)
#        except socket.error:
#            print("Connection lost.")
#            time.sleep(5)
#            continue
