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
    gen = 0    

    ui_helper = None
    while True:
 
        gen += 1
        players = list()
        threads = list()

        for index in range(12): 
            brain = None
            if winner is not None:
                brain = deepcopy(winner.brain)
                brain.random(index ** 2)
            player = Player(brain)
            players.append(player)
            threads.append(Processor(player))
        
        if ui_helper is None:
            ui_helper = ThreadHelper(players)
            ui_helper.start()
        else:
            ui_helper.update(players)

        ui_helper.event.wait()
        for thread in threads:
            thread.sg = ui_helper.sg
            thread.start()

        for thread in threads:
            thread.join()
    
        print('Gen: %s, The winner is: %s' % (gen, winner))

    


class ThreadHelper(threading.Thread):

    def __init__(self, players):
        super().__init__()
        self.players = players
        self.event = threading.Event()
        self.event.clear()

    def update(self, players):
        self.players = players
        self.sg.setGames([p.game for p in players])

    def run(self):
        app = QApplication(sys.argv)
        self.sg = SnakeGui([p.game for p in self.players])
        self.event.set()
        self.sg.show()
        app.exec_()


class Processor(threading.Thread):

    sg = None

    def __init__(self, player):
        super().__init__()
        self.player = player

    def run(self):

        if not self.player.step():
            print('Game over')
            print('Score: %s Used directions: %s' % (self.player.game.score, len(self.player.used_directions)))
            global winner
            if len(self.player.used_directions) < 2:
                return
            if winner is None:
                winner = self.player
            elif winner.used_directions < self.player.used_directions:
                print(winner.used_directions +'/'+ self.player.used_directions)
                winner = self.player
            elif winner.game.score < self.player.game.score:
                 winner = self.player
            return
        self.sg.update()
        self.run()







