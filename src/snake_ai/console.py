import sys
import gc
import time
import pickle
import datetime
import threading
import collections
import multiprocessing

from copy import deepcopy
from random import random
from snake_ai.widget import  SnakeGui
from snake_ai.game import Game
from snake_ai.brain import Brain
from snake_ai.brain import Player

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt



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


def show():
    if len(sys.argv) != 2:
        print('path to brain file must given as argument')
        sys.exit(1)
    path = sys.argv[1]
    brain = pickle.load(open(path, 'rb' ))
    print(brain.show())

def ai():
    brain = None
    if len(sys.argv) == 2:
        brain = pickle.load(open(sys.argv[1], 'rb'))
        print('brain loaded from: %s' % sys.argv[1])
    MainAI(brain).run()

class MainAI(object):
     
    amount_process = 30
    dump_name = '%s.brain.dump' % datetime.datetime.today().strftime('%Y%m%d_%H%M')

    def __init__(self, brainfile=None):
        self.winner = None
        self.players = collections.OrderedDict()
        self.brainfile = brainfile


    def prepare_process(self, args):
        index, brain = args

        if brain is None and self.brainfile is not None:
            brain = self.brainfile

        if brain is not None:
            index = float(index)
            brain.random((index**2/self.amount_process**2)*100)
        else:
            brain = Brain([30*25*3, 500, 200, 4])
            brain.random()
        return brain

    def run(self):
        gen = 0
        ui_helper = None
        while True:
            self.players.clear()
            gen += 1
            threads = list()

            pool = multiprocessing.Pool()
            brain = None
            if self.winner is not None:
                brain = self.winner.brain
            brains = pool.map(self.prepare_process, [(i, brain,) for i in range(self.amount_process)])
            pool.close()
 
            for brain in brains:
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

                print('Score: %s Used directions: %s' % (thread.player.game.score, len(thread.player.used_directions)))

                if thread.main.winner is None:
                    thread.main.winner = thread.player

                if len(thread.main.winner.used_directions) < len(thread.player.used_directions):
                    thread.main.winner = thread.player
                    continue

                if thread.main.winner.game.score < thread.player.game.score and len(thread.main.winner.used_directions) <= len(thread.player.used_directions):
                    thread.main.winner = thread.player

            if self.winner is not None:
                pickle.dump(self.winner.brain, open(self.dump_name, 'wb'))
                print('Gen: %s, The winner is: %s score: %s used directions: %s' % (gen, self.winner, self.winner.game.score, len(self.winner.used_directions)))
            else:
                print('Gen %s has no winner' % gen)
    


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

    def start(self):
        super().start()
        self.worker.start()

    def run(self):
        while True:
            self.player, brain = self.queue.get()
            self.main.players[self.player.uuid] = self.player
            self.sg.setGames([p.game for p in self.main.players.values()])
            if brain is not None:
                self.player.brain = brain
                break
            self.sg.update()
            time.sleep(0.2)
        self.sg.update()

        self.queue.close()
        self.worker.join()


class ProcessorWorker(multiprocessing.Process):

    def __init__(self, player, queue):
        super().__init__()

        self.player = player
        self.queue = queue

    def run(self):
        while True:
            re = self.player.step()
            if re:
                self.queue.put((self.player, None,))
            else:
                self.queue.put((self.player, self.player.brain,))
                break




