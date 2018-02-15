import sys

from snake_ai import game

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, QEvent

class SnakeGui(QMainWindow):
    
    def __init__(self, game):
        super().__init__()
        
        self.game = game
        self.keylistener = None
        self.initUI()
        
        
    def initUI(self):      
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Snake Playing Game')
       

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        self.drawPlayingField(event, qp)
        qp.end()
        
        
    def drawPlayingField(self, event, qp):
        print('draw gui')
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


    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            if self.keylistener is not None:
                self.keylistener(event.key())
        return super().keyPressEvent(event)


