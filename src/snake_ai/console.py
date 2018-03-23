import sys
import threading
import multiprocessing
import collections

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


def ai():
    MainAI().run()


class MainAI(object):

    def __init__(self):
        self.winner = None
        self.players = collections.OrderedDict()


    def run(self):
        gen = 0    

        ui_helper = None
        while True:

            gen += 1
            threads = list()

            for index in range(30): 
                brain = None
                if self.winner is not None:
                    brain = deepcopy(self.winner.brain)
                    brain.random((index**4)/(10**4)*index)
                player = Player(brain)
                self.players[player.uuid] = player
                threads.append(Processor(player, self))
        
            if ui_helper is None:
                ui_helper = ThreadHelper(self.players)
                ui_helper.start()
            else:
                ui_helper.update(self.players)

            ui_helper.event.wait()
            for thread in threads:
                thread.sg = ui_helper.sg
                thread.start()

            for thread in threads:
                thread.join()
    
            print('Gen: %s, The winner is: %s' % (gen, self.winner))

    


class ThreadHelper(threading.Thread):

    def __init__(self, players):
        super().__init__()
        self.players = players
        self.event = threading.Event()
        self.event.clear()

    def update(self, players):
        self.players = players
        self.sg.setGames([p.game for p in players.values()])

    def run(self):
        app = QApplication(sys.argv)
        self.sg = SnakeGui([p.game for p in self.players.values()])
        self.event.set()
        self.sg.show()
        app.exec_()


class Processor(threading.Thread):

    sg = None

    def __init__(self, player, main):
        super().__init__()
        self.player = player
        self.main = main
        self.queue = multiprocessing.Queue()
        self.worker = ProcessorWorker(player, self.queue)

    def run(self):
        self.worker.start()
        while True:
            re = self.queue.get()
            if isinstance(re, Player):
                self.player = re
                self.main.players[self.player.uuid] = self.player
                self.sg.setGames([p.game for p in self.main.players.values()])
            else:
                self.player.brain = re
                print('Game over')
                print('Score: %s Used directions: %s' % (self.player.game.score, len(self.player.used_directions)))
                if len(self.player.used_directions) < 2:
                    return
                if self.main.winner is None:
                    self.main.winner = self.player
                elif len(self.main.winner.used_directions) < len(self.player.used_directions):
                    print('best used direction: %s/%s' % (len(self.main.winner.used_directions), len(self.player.used_directions)))
                    self.main.winner = self.player
                elif self.main.winner.game.score < self.player.game.score:
                    print('best score: %s/%s' % (self.main.winner.game.score, self.player.game.score))
                    self.main.winner = self.player
                return
            self.sg.update()


class ProcessorWorker(multiprocessing.Process):

    def __init__(self, player, queue):
        super().__init__()
        self.player = player
        self.queue = queue


    def run(self):
        while True:
            re = self.player.step()
            self.queue.put(self.player)
            if not re:
                self.queue.put(self.player.brain)
                self.queue.close()
                break





