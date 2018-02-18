import sys
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
    timer.setInterval(400)
    timer.timeout.connect(processor)
    timer.start()

    sg.keylistener = keylistener
    sg.show()
    sys.exit(app.exec_())



def ai():
    app = QApplication(sys.argv)
    
    players = list()
    timers = list()

    sg = None
    for index in range(12): 
        player = Player()
        players.append(player)
        def processor():
            if not player.step():
                print('Game over')
                print('Score: %s' % player.game.score)
                #sys.exit()
            sg.update()

        timer = QTimer()
        timer.setInterval(1000)
        timer.timeout.connect(processor)
        timers.append(timer)
    
    sg = SnakeGui([p.game for p in players])
    for timer in timers:
        timer.start()

    sg.show()
    sys.exit(app.exec_())




