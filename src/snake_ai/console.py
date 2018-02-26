import sys
import threading
from multiprocessing import Process, Manager

from copy import deepcopy
from random import random
from snake_ai.widget import  SnakeGui
from snake_ai.game import Game
from snake_ai.brain import Player

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt
import numpy as np



def play():

    app = QApplication(sys.argv)


    game = Game(25, 20) 
    sg = SnakeGui(game)

    def keylistener(key):
        if Qt.Key_Up == key:
            game.up()
        if Qt.Key_Down == key:
            game.down()
        if Qt.Key_Left == key:
            game.left()
        if Qt.Key_Right == key:
            game.right()

    def processor():
        if not game.move():
            print('Game over')
            print('Score: %s' % game.score)
            sys.exit()
        sg.update()

    timer = QTimer()
    timer.setInterval(200)
    timer.timeout.connect(processor)
    timer.start()

    sg.keylistener = keylistener
    sg.show()
    sys.exit(app.exec_())


winner = None
def ai():
    gen = 0    

    ui_helper = None
    gns = Manager().Namespace()
    gns.winner = None

    while True: 
        gen += 1
        players = list()
        threads = list()

        for index in range(50): 
            brain = None
            if gns.winner is not None:
                brain = gns.winner.brain
                brain.random((index**4)/(10**4)*index)
            player = Player(brain)
            manager = Manager()
            ns = manager.Namespace()
            ns.game = player.game
            ns.used_directions = player.used_directions
            ns.test = 0
            players.append(ns)
            threads.append(Processor(ns, gns, player))
        
        if ui_helper is None:
            ui_helper = ThreadHelper(players)
            ui_helper.start()
            ui_helper.event.wait()
        else:
            ui_helper.update(players)

        for thread in threads:
            thread.sg = ui_helper.sg
            thread.start()

        for thread in threads:
            thread.join()
    
        print('Gen: %s, The winner is: %s' % (gen, gns.winner))



class ThreadHelper(threading.Thread):

    def __init__(self, players):
        super().__init__()
        self.players = players
        self.event = threading.Event()
        self.event.clear()

    def update(self, players):
        self.players = players
        self.sg.update()

    def timer(self):
        self.sg.setGames([ns.game for ns in self.players])
        self.sg.update()


    def run(self):
        app = QApplication(sys.argv)
        self.sg = SnakeGui([ns.game for ns in self.players])
        self.sg.show()
        self.event.set()
        timer = QTimer()
        timer.timeout.connect(self.timer)
        timer.start(100)
        app.exec_()


class Processor(Process):

    sg = None

    def __init__(self, ns, gns, player):
        super().__init__()
        self.ns = ns
        self.gns = gns
        self.player = player

    def run(self):
        while True:
            ret = self.player.step()
            self.ns.test += 1
            self.ns.game = self.player.game
            self.ns.used_directions = self.player.used_directions

            if not ret:
                winner = self.gns.winner
                print('Game over')
                print('Score: %s Used directions: %s' % (self.player.game.score, len(self.player.used_directions)))
                if len(self.player.used_directions) < 2:
                    return
                if winner is None:
                    self.gns.winner = self.player
                elif len(winner.used_directions) < len(self.player.used_directions):
                    print('best used direction: %s/%s' % (len(winner.used_directions), len(self.player.used_directions)))
                    self.gns.winner = self.player
                elif winner.game.score < self.player.game.score:
                    print('best score: %s/%s' % (winner.game.score, self.player.game.score))
                    self.gns.winner = self.player
                return







