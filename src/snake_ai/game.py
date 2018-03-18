import uuid
import operator
from random import random


FIELD_APPLE = 0
FIELD_WALL = 1
FIELD_SNAKE = 2
FIELD_EMPTY = 3

MOVE_UP = 0, -1
MOVE_DOWN = 0, 1
MOVE_LEFT = -1, 0
MOVE_RIGHT = 1, 0


SNAKE_INIT_GROW = 3

class Game(object):

    def __init__(self, width, height):
        self.uuid = uuid.uuid1()
        self.width = width
        self.height = height
        self.score = 0
        self.snake = list()
        self.snake_grow = SNAKE_INIT_GROW
        self.direction = MOVE_UP
        self.field = [[0 for x in range(height)] for y in range(width)] 

        for i in range(width):
            for j in range(height):
                self.field[i][j] = FIELD_EMPTY
                if i == 0 or i == self.width -1  or j == 0 or j == self.height -1:
                    self.field[i][j] = FIELD_WALL
        
        self.apple()
        self.init_snake()

    def state(self):
        for t in (FIELD_SNAKE, FIELD_WALL, FIELD_APPLE):
            output = list()
            for i in range(self.width):
                for j in range(self.height):
                    yield self.field[i][j] == t


    def apple(self):
        x,y = self.random_point()
        self.field[x][y] = FIELD_APPLE


    def init_snake(self):
        self.snake.append(self.random_point())
        self.display_snake()


    def display_snake(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.field[i][j] == FIELD_SNAKE:
                    self.field[i][j] = FIELD_EMPTY

        for x,y in self.snake:
            self.field[x][y] = FIELD_SNAKE


    def random_point(self):
        while True:
            x,y = int(random() * self.width), int(random() * self.height)
            if self.field[x][y] == FIELD_EMPTY:
                return x,y


    def move(self):
        self.score += 1
        head = self.snake[-1:][0]
        new = tuple(map(operator.add, head, self.direction))
        x,y = new
        if self.field[x][y] in (FIELD_WALL, FIELD_SNAKE):
            return False

        self.snake.append(new)
        if self.snake_grow <= 0:
            self.snake = self.snake[1:]
        else:
            self.snake_grow -= 1

        if self.field[x][y] == FIELD_APPLE:
            self.eat(x, y)

        self.display_snake()
        return True


    def eat(self, x, y):
        self.field[x][y] = FIELD_SNAKE
        self.apple()
        self.snake_grow += 1
        self.score += 100


    def up(self):
        self.direction = MOVE_UP


    def down(self):
        self.direction = MOVE_DOWN


    def left(self):
        self.direction = MOVE_LEFT


    def right(self):
        self.direction = MOVE_RIGHT





