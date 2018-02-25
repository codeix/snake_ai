import sys
import math

from snake_ai import game

from PyQt5.QtWidgets import QMainWindow, QApplication, QGridLayout, QGroupBox, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, QEvent



class SnakeGui(QWidget):
    
    def __init__(self, games):
        super().__init__()
        self.setGeometry(300, 300, 2000, 1700)
        self.setWindowTitle('Snake Playing Game')

        if not isinstance(games, (list, tuple)):
            games = [games]

        self.games = None 
        self.canvas = None
        self.keylistener = None
        self.initUI(games)
        
        
    def initUI(self, games):
        self.games = games
        self.canvas = [GameCanvas(g) for g in self.games]
        self.setGeometry(300, 300, 2000, 1700)
        self.setWindowTitle('Snake Playing Game')
        
        x = math.sqrt(len(self.canvas))
        y = x if x % 1 == 0 else x + 1 
        
        temp_canvas = [] + self.canvas

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        for ix in range(int(x)):
            for iy in range(int(y)):
                if not len(temp_canvas):
                    continue
                self.layout.addWidget(temp_canvas.pop(), ix, iy)


    def setGames(self, games):
        temp = games + []
        if self.layout is not None:
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    widget.game = temp.pop()


    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            if self.keylistener is not None:
                self.keylistener(event.key())
        return super().keyPressEvent(event)


class GameCanvas(QWidget):

    def __init__(self, game):
        super().__init__()
        self.game = game


    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawPlayingField(event, qp)
        qp.end()
        
        
    def drawPlayingField(self, event, qp):
        qp.fillRect(event.rect(), QBrush(Qt.white))
        qp.setPen(QColor(Qt.white))
        qp.setBrush(Qt.black)

        rect = event.rect()

        for x, row in enumerate(self.game.field):
            for y, cell in enumerate(row):
                if cell == game.FIELD_WALL:
                    qp.setBrush(Qt.black)
                if cell == game.FIELD_EMPTY:
                    qp.setBrush(Qt.white)
                if cell == game.FIELD_APPLE:
                    qp.setBrush(Qt.red)
                if cell == game.FIELD_SNAKE:
                    qp.setBrush(Qt.blue)
                qp.drawRect(*self.indexToCoord(rect.width(), rect.height(), x, y))


    def indexToCoord(self, width, height, x, y):
        lx = width / self.game.width
        ly = height / self.game.height
        return lx * x, ly * y, lx, ly



