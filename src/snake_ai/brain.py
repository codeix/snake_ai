import uuid
from random import random
from snake_ai.game import Game



class Player(object):

    def __init__(self, brain = None):
        self.uuid = uuid.uuid1()
        self.game = Game(30, 25)
        self.used_directions = set()
        if brain is None:
            self.brain = Brain([30*25*3, 200, 200, 200, 50, 4])
            self.brain.random()
        else:
            self.brain = brain

    def __getstate__(self):
        state = dict(self.__dict__)
        del state['brain']
        return state


    def step(self):
        out = self.brain.apply(self.game.state())
        direction = dict(zip((self.game.up, self.game.down, self.game.left, self.game.right, ), out))
        func = max(direction, key=direction.get)
        func()
        self.used_directions.add(func)
        return self.game.move()




class Brain(object):
    
    def __init__(self, layers):
        self.neurons = list()
        self.layers = list()
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

        len(self.layers)
        for layer in self.layers:
            for neuron in layer:
                neuron.submit()

        output = self.layers[-1:][0]
        return tuple([i.value/i.max_weight for i in output])
         

    def random(self, percentage=None):
        for neuron in self.neurons:
            neuron.random(percentage)
    

    def set_weights(self, value):
       for neuron in self.neurons:
            neuron.set_weights(value)


    def reset(self):
        for neuron in self.neurons:
            neuron.reset()


class Neuron(object):
    
    def __init__(self, parents):
        self.weights = None
        self.value = 0
        self.max_weight = 0

        if parents is not None:
            self.weights = dict()
            for parent in parents:
                self.weights[parent] = 0


    def reset(self):
        self.value = 0


    def random(self, percentage):
        if self.weights is None:
            return
        for k in self.weights.keys():
            if percentage is None:
                self.weights[k] = random()
            else:
                new = random()
                new = self.weights[k] + (random()/100*percentage) - (percentage/100.0/2)
                new = min(new, 1)
                new = max(new, 0)
                self.weights[k] = new


    def set_weights(self, value):
        if self.weights is None:
            return
        for k in self.weights.keys():
            self.weights[k] = value


    def apply(self, value):
        self.value += value


    def submit(self):
        if self.weights is None:
            return
        for neuron, weight in self.weights.items():
            neuron.apply(self.value * weight)



