import sys
import gc
import time
import json
import code
import pickle
import argparse
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
        if Qt.Key_Space == key:
            if timer.isActive():
                timer.stop()
            else:
                timer.start()

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

def read_brain_ctl():
    if len(sys.argv) != 2:
        print('path to brain file must given as argument')
        sys.exit(1)
    path = sys.argv[1]
    return pickle.load(open(path, 'rb' )), path

def read_multi_brain_ctl():
    if len(sys.argv) <= 1:
        print('at least one path to brain must given')
        sys.exit(1)
    brains = list()
    for i in range(1, len(sys.argv)):
        path = sys.argv[i]
        brains.append(pickle.load(open(path, 'rb' )))
    return brains, sys.argv[1]

def show():
    brain, path = read_brain_ctl()
    print(brain.show())

def console():
    brain, path = read_brain_ctl()
    def save(name):
        if not name:
            raise "name is empty"
        pickle.dump(brain, open('%s.brain.dump' % name, 'wb'))
    code.interact(banner='You can access the brain with the global "brain".\n Use the method "save(name)" to save the brain as file with the given name.',
            local=dict(brain=brain, save=save))

def export():
    posfactorx = 1000.
    posfactory = 100.
    brains, path = read_multi_brain_ctl()
    brain = brains.pop(0)
    nodes = list()
    edges = list()
    uuids = dict()
    positions = dict()

    for index, node in enumerate(brain.inputs):
        positions[node] = dict(x=0, y=index*posfactory)

    for xi, layer in enumerate(brain.layers):
        for yi, node in enumerate(layer):
            positions[node] = dict(x=(xi+1)*posfactorx, y=yi*posfactory)

    for dbrain in brains:
        uuids[dbrain] = dict([(b.uuid, b) for b in itertools.chain(dbrain.inputs, dbrain.neurons())])

    for node in itertools.chain(brain.inputs, brain.neurons()):
        jsnode = {
                "data" : {
                    "id" : str(node.uuid),
                    "shared_name" : node.name(),
                    "name" : node.name(),
                    "SUID" : id(node),
                    "type" : node.__class__.__name__,
                    "selected" : False
                    },
                "position" : positions[node],
                "selected" : False
                }
        nodes.append(jsnode)
        if not hasattr(node, 'weights') or node.weights is None:
            continue
        for index, (rel, weight) in enumerate(node.weights.items()):
            jsedge = {
                    "data" : {
                    "id" : str(index),
                    "source" : str(rel.uuid),
                    "target" : str(node.uuid),
                    "shared_name" : f"{rel.name()} to {node.name()}",
                    "name" : f"{rel.name()} to {node.name()}",
                    "interaction" : "interacts with",
                    "SUID" : index,
                    "weight" : weight,
                    "shared_interaction" : "interacts with",
                    "selected" : False
                    }
                    }
            edges.append(jsedge)

            for dindex, dbrain in enumerate(brains):
                dweight = list(uuids[dbrain][node.uuid].weights.values())[index]
                diff = dweight - weight
                jsedge['data']['diff%s' % dindex] = diff

    output = {"format_version" : "1.0",
            "generated_by" : "cytoscape-3.7.2",
            "target_cytoscapejs_version" : "~2.1",
            "data" : {
                "shared_name" : path,
                "name" : path,
                "SUID" : 728,
                "__Annotations" : [ ],
                "selected" : True
                },
            "elements" : {
                "nodes": nodes,
                "edges": edges}}
    with open(f'{path}.cyjs', 'w') as fp:
        json.dump(output, fp)





def ai():
    parser = argparse.ArgumentParser(description="Playing Snake Game")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-g", "--gui-less", action="store_true", help="Run without GUI")
    parser.add_argument("brainfile", type=str, nargs='?', help="path to pickle brain file", default=None)
    args = parser.parse_args()

    brain = None
    if args.brainfile is not None:
        brain = pickle.load(open(args.brainfile, 'rb'))
        print('brain loaded from: %s' % args.brainfile)
    MainAI(brain, not args.gui_less).run()

class MainAI(object):
     
    amount_process = 30
    dump_name = '%s.brain.dump' % datetime.datetime.today().strftime('%Y%m%d_%H%M')

    def __init__(self, brainfile=None, has_gui=True):
        self.childs = None
        self.players = collections.OrderedDict()
        self.brainfile = brainfile
        self.has_gui = has_gui

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

            if self.childs is None:
                if self.brainfile is None:
                    self.childs = [Brain([8*3, 20, 4]) for i in range(self.amount_process)]
                else:
                    self.childs = [self.brainfile for i in range(self.amount_process)]
 
            for index, brain in enumerate(self.childs):
                player = Player(brain, seed)
                self.players[player.uuid] = player
                threads.append(Processor(index, player, self))

            if self.has_gui:
                if ui_helper is None:
                    ui_helper = ThreadHelper(self.players)
                    ui_helper.start()
                else:
                    ui_helper.update(self.players)
                ui_helper.event.wait()
            
            for thread in threads:
                if self.has_gui:
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
        with ProcessorWorker.get_process(self.player, self.sg is not None) as queue:
            while True:
                self.player, brain = queue.get()
                self.main.players[self.player.uuid] = self.player
                if self.sg is not None:
                    self.sg.setGame(self.player.game, self.index)
                if brain is not None:
                    self.player.brain = brain
                    break
                if self.sg is not None:
                    self.sg.update(self.index)
            if self.sg is not None:
                self.sg.update(self.index)


class ProcessorWorker(multiprocessing.Process):

    MAX_SLEEP_TIME = 0.08

    pool = list()
    lock = threading.RLock()


    def __init__(self, has_gui):
        super().__init__()

        self.running = False
        self.player = None
        self.has_gui = has_gui
        self.queue = multiprocessing.Queue()
        self.controller = multiprocessing.Queue()

    @staticmethod
    def get_process(player, has_gui):
        process = None
        with ProcessorWorker.lock:
            nonrunning = [i for i in ProcessorWorker.pool if not i.running]
            if len(nonrunning) > 0:
                process = nonrunning[0]
            else:
                process = ProcessorWorker(has_gui)
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
            player.brain.random(0.5)
            while True:
                started = time.time()
                re = player.step()
                if re:
                    self.queue.put((player, None,))
                else:
                    self.queue.put((player, player.brain,))
                    break
                if self.has_gui:
                    time.sleep(max(self.MAX_SLEEP_TIME - time.time() + started, 0))

