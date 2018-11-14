import os
import sys
import neat
import time
import pickle
import argparse
import datetime
import itertools
import threading
import collections
import multiprocessing

import numpy as nu
from random import random
from snake_ai.widget import  SnakeGui
from snake_ai.game import Game
from snake_ai.brain import Brain
from snake_ai.brain import Player

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer, Qt

try:
    # pylint: disable=import-error
    import Queue as queue
except ImportError:
    # pylint: disable=import-error
    import queue


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


class GuiThread(threading.Thread):


    def __init__(self):
        super().__init__()
        self.event = threading.Event()
        self.event.clear()
        self.sleeptime = 0.1
        self.update_gui = True

    def run(self):

        def keylistener(key):
            if Qt.Key_Up == key:
                self.sleeptime += 0.01
            if Qt.Key_Down == key:
                self.sleeptime = max(0, self.sleeptime-0.01)
            if Qt.Key_Left == key:
                self.update_gui = False
            if Qt.Key_Right == key:
                self.update_gui = True


        app = QApplication(sys.argv)
        self.sg = SnakeGui([Game(25, 25) for i in range(30)])
        self.sg.keylistener = keylistener
        self.event.set()
        self.sg.show()
        app.exec_()

guiThread = None

def eval_genome(genome_id, genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    fitnesses = []

    for runs in range(5):
        gui_id = (genome_id - 1) % 30
        game = Game(25, 20)
        guiThread.sg.setGame(game, gui_id)
        guiThread.sg.update()

        # Run the given simulation for up to num_steps time steps.
        fitness = 0.0
        while game.move():
            inputs = game.state()
            action = net.activate(list(inputs))
            
            # Apply action to the simulated cart-pole
            direction = dict(zip((game.up, game.down, game.left, game.right, ), action))
            func = max(direction, key=direction.get)
            func()
            fitness = game.score
            if guiThread.update_gui:
                time.sleep(guiThread.sleeptime)
                guiThread.sg.update(gui_id)

        guiThread.sg.update(gui_id)
        fitnesses.append(fitness)

    # The genome's fitness is its worst performance across all runs.
    return nu.median(fitnesses)


def eval_genomes(genomes, config):
    print('\n\n')
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome_id, genome, config)
        print('Genome<%s>: %s fitness' % (genome_id, genome.fitness))

class ParallelEvaluator(neat.ParallelEvaluator):
    def evaluate(self, genomes, config):
        jobs = []
        for genome_id, genome in genomes:
            jobs.append(self.pool.apply_async(self.eval_function, (genome, config, genome_id)))

        # assign the fitness back to each genome
        for job, (ignored_genome_id, genome) in zip(jobs, genomes):
            genome.fitness = job.get(timeout=self.timeout)

class ThreadedEvaluator(neat.ThreadedEvaluator):
    def _worker(self):
        """The worker function"""
        while self.working:
            try:
                genome_id, genome, config = self.inqueue.get(
                    block=True,
                    timeout=0.2,
                    )
            except queue.Empty:
                continue
            f = self.eval_function(genome_id, genome, config)
            self.outqueue.put((genome_id, genome, f))

def ai():
    global guiThread
    guiThread = GuiThread()
    guiThread.start()
    guiThread.event.wait()

    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path) 

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))


    th = ThreadedEvaluator(30, eval_genome)
    #pe = ParallelEvaluator(12, eval_genome)
    winner = pop.run(th.evaluate)#pop.run(eval_genomes)#pop.run(pe.evaluate)
    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)



