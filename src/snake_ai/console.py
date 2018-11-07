import sys
import gc
import time
import pickle
import datetime
import itertools
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
        print([i for i in game.state()])
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
        self.childs = None
        self.players = collections.OrderedDict()
        self.brainfile = brainfile


    def prepare_process(self, args):
        index, brain = args

        if brain is None and self.brainfile is not None:
            brain = self.brainfile

        if brain is not None:
            index = float(index)
            brain.random(0.5)
            #brain.random((index**2/self.amount_process**2)*100)
        else:
            brain = Brain([8*3, 20, 4])
        return brain

    def run(self):
        gen = 0
        ui_helper = None
        started = None

        while True:
            started = time.time()
            self.players.clear()
            seed = 10#random()
            gen += 1
            threads = list()

            pool = multiprocessing.Pool()
            brains = None
            if self.childs is not None:
                brains = pool.map(self.prepare_process, [(i, brain,) for i, brain in enumerate(self.childs)])
            else:
                brains = pool.map(self.prepare_process, [(i, None,) for i in range(self.amount_process)])
            pool.close()
 
            for index, brain in enumerate(brains):
                player = Player(brain, seed)
                self.players[player.uuid] = player
                threads.append(Processor(index, player, self))

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

            threads.sort(reverse=True, key=lambda t: (not t.player.game.killed, len(t.player.used_directions), len(t.player.game.snake), t.player.game.steps))


            print('\n\n\nGen: %s, Sec.: %.3f' % (gen, time.time() - started))
            for thread in threads:
                print('Score: %s Used directions: %s steps: %s snake length: %s crossovered: %s' % (
                thread.player.game.score,
                len(thread.player.used_directions),
                thread.player.game.steps,
                len(thread.player.game.snake),
                getattr(thread.player.brain, 'crossovered', '')))

                thread.player.brain.crossovered = False

            bests = threads[:3]
            childs = [t.player.brain for t in threads]
            for pairs in itertools.combinations(bests, 2):
                leftP, rightP = pairs
                left, right = (leftP.player.brain, rightP.player.brain)
                ca, cb = Brain.crossover(left, right)
                childs.insert(0, ca)
                childs.insert(0, cb)
            self.childs = childs[:self.amount_process]
            
            pickle.dump(childs[0], open(self.dump_name, 'wb'))    


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

    def __init__(self, index, player, main):
        super().__init__()
        self.index = index
        self.player = player
        self.main = main

    def run(self):
        with ProcessorWorker.get_process(self.player) as queue:
            while True:
                self.player, brain = queue.get()
                self.main.players[self.player.uuid] = self.player
                self.sg.setGame(self.player.game, self.index)
                if brain is not None:
                    self.player.brain = brain
                    break
                self.sg.update(self.index)

            self.sg.update(self.index)


class ProcessorWorker(multiprocessing.Process):

    MAX_SLEEP_TIME = 0.08

    pool = list()
    lock = threading.RLock()


    def __init__(self):
        super().__init__()

        self.running = False
        self.player = None
        self.queue = multiprocessing.Queue()
        self.controller = multiprocessing.Queue()

    @staticmethod
    def get_process(player):
        process = None
        with ProcessorWorker.lock:
            nonrunning = [i for i in ProcessorWorker.pool if not i.running]
            if len(nonrunning) > 0:
                process = nonrunning[0]
            else:
                process = ProcessorWorker()
                ProcessorWorker.pool.append(process)
                process.start()
            process.player = player
        return process
                
    def __enter__(self):
        with ProcessorWorker.lock:
            self.running = True
            self.controller.put((self.player, self.player.brain,))
        return self.queue

    def __exit__(self, type, value, traceback):
        with ProcessorWorker.lock:
            self.running = False
        return isinstance(value, TypeError)

    def run(self):
        while True:
            player, brain = self.controller.get()
            player.brain = brain
            while True:
                started = time.time()
                re = player.step()
                if re:
                    self.queue.put((player, None,))
                else:
                    self.queue.put((player, player.brain,))
                    break
                time.sleep(max(self.MAX_SLEEP_TIME - time.time() + started, 0))




