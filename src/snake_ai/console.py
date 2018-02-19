import sys
import threading

from random import random
from snake_ai.widget import  SnakeGui
from snake_ai.game import Game
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



def ai():
    app = QApplication(sys.argv)
    
    players = list()
    threads = list()

    for index in range(12): 
        player = Player()
        players.append(player)
        threads.append(Processor(player))
    
    sg = SnakeGui([p.game for p in players])
    for thread in threads:
        thread.sg = sg
        thread.start()

    sg.show()
    sys.exit(app.exec_())


class Processor(threading.Thread):

    sg = None

    def __init__(self, player):
        super().__init__()
        self.player = player

    def run(self):

        if not self.player.step():
            print('Game over')
            print('Score: %s' % self.player.game.score)
            
            return
        self.sg.update()
        self.run()







