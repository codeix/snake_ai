from random import random
from snake_ai.game import Game



class Player(object):

    def __init__(self):
        self.game = Game(30, 25)
        self.brain = Brain([30*25*3, 4])
        self.brain.random()

    def step(self):
        out = self.brain.apply(self.game.state())
        direction = dict(zip((self.game.up, self.game.down, self.game.left, self.game.right, ), out))
        max(direction, key=direction.get)()
        return self.game.move()




class Brain(object):
    
    neurons = list()
    layers = list()


    def __init__(self, layers):
        layers.reverse()
        for layer_size in layers:
            li = list()
            for i in range(layer_size):
                last = self.layers[:1]
                if last:
                    last = last.pop()
                else:
                    last = None
                li.append(Neuron(last))
            self.neurons += li
            self.layers.insert(0, li)

        weight_sum = 1
        for layer in self.layers:
            new_weight_sum = 0
            for neuron in layer:
                neuron.max_weight = weight_sum
                new_weight_sum += neuron.max_weight
            weight_sum = new_weight_sum


    def apply(self, inputs):
        self.reset()
         
        for index, value in enumerate(inputs):
            self.layers[0][index].apply(value)
       
        for layer in self.layers:
            for neuron in layer:
                neuron.submit()


        output = self.layers[-1:][0]
        return tuple([i.value/i.max_weight for i in output])
         

    def random(self):
        for neuron in self.neurons:
            neuron.random()

    def reset(self):
        for neuron in self.neurons:
            neuron.reset()


class Neuron(object):
    
    weights = None
    value = 0
    max_weight = 0

    def __init__(self, parents):
        if parents is not None:
            self.weights = dict()
            for parent in parents:
                self.weights[parent] = 0


    def reset(self):
        self.value = 0


    def random(self):
        if self.weights is None:
            return
        for k in self.weights.keys():
            self.weights[k] = random()


    def apply(self, value):
        self.value += value


    def submit(self):
        if self.weights is None:
            return
        for neuron, weight in self.weights.items():
            neuron.apply(self.value * weight)


