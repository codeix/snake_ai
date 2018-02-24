import sys
import threading

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
    app = QApplication(sys.argv)
    gen = 0    

    while True:
 
        gen += 1
        players = list()
        threads = list()

        for index in range(12): 
            brain = None
            if winner is not None:
                brain = deepcopy(winner.brain)
                brain.random(index)
            player = Player(brain)
            players.append(player)
            threads.append(Processor(player))
    
        sg = SnakeGui([p.game for p in players])
        for thread in threads:
            thread.sg = sg
            thread.start()

        sg.show()
    
        helper = ThreadHelper(threads, sg)
        helper.start()
        app.exec_()
        print('Gen: %s, The winner is: %s' % (gen, winner))

    


class ThreadHelper(threading.Thread):

    def __init__(self, threads, sg):
        super().__init__()
        self.threads = threads
        self.sg = sg

    def run(self):
        for thread in self.threads:
            thread.join()
        self.sg.close()


class Processor(threading.Thread):

    sg = None

    def __init__(self, player):
        super().__init__()
        self.player = player

    def run(self):

        if not self.player.step():
            print('Game over')
            print('Score: %s Variance: %s' % (self.player.game.score, np.var(self.player.lastout)))
            global winner
            if winner is None:
                winner = self.player
            elif np.var(self.player.lastout) > 1.5:
                return
            elif winner.game.score < self.player.game.score:
                 winner = self.player
            return
        self.sg.update()
        self.run()







