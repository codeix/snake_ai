import uuid
import itertools
import  numpy as nu
from random import random
from snake_ai.game import Game



class Player(object):

    def __init__(self, brain = None, seed=None):
        self.uuid = uuid.uuid1()
        self.game = Game(30, 25, seed)
        self.used_directions = set()
        if brain is None:
            self.brain = Brain([30*25*3, 500, 500, 50, 4])
            self.brain.random()
        else:
            self.brain = brain

    def __getstate__(self):
        state = dict(self.__dict__)
        del state['brain']
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self.brain = None


    def step(self):
        out = self.brain.apply(self.game.state())
        print(out)
        direction = dict(zip((self.game.up, self.game.down, self.game.left, self.game.right, ), out))
        func = max(direction, key=direction.get)
        func()
        self.used_directions.add(func)
        return self.game.move()


class AbstractNeuron(object):

    def __init__(self):
        self.weights = None
        self.cache = None

    def relations(self, neurons, default_weight=0):
        self.weights = dict()
        for neuron in neurons:
            self.weights[neuron] = default_weight

    def random(self, percentage):
        for k in self.weights.keys():
            if percentage is None:
                self.weights[k] = random()
            else:
                new = self.weights[k] + (random()/100*percentage) - (percentage/100.0/2)
                new = min(new, 1)
                new = max(new, 0)
                self.weights[k] = new

    def set_weights(self, value):
        for k in self.weights.keys():
            self.weights[k] = value

    def activation(self, value):
        raise Exception('need to be overridden')

    def reset(self):
        self.cache = None

    def apply(self):
        if self.cache is None:
            summary = 0
            for neuron, weight in self.weights.items():
                summary += neuron.apply() * weight
            self.cache = self.activation(summary)
        return self.cache

    def __repr__(self):
        return '%s<%s>' % (self.__class__.__name__, ','.join(map(str, self.weights.values())))


class InputNeuron(AbstractNeuron):

    def __init__(self, index, data):
        self.index = index
        self.data = data

    def apply(self):
        return self.data.get(self.index)


class TanHNeuron(AbstractNeuron):

    def activation(self, value):
         return nu.tanh(value)


class Brain(object):
    
    def __init__(self, structure, classNeuron=TanHNeuron):
        self.layers = list()
        self.inputs = Layer()
        self.data = Data()

        for i in range(structure[0]):
            self.inputs.append(InputNeuron(i, self.data))

        for size in structure:
            layer = Layer()
            self.layers.append(layer)
            for i in range(size):
                 layer.append(classNeuron())

        for index in range(len(self.layers) -1, -1, -1):
            layer = self.layers[index]
            if (index > 0):
                prev_layer = self.layers[index-1]
                for neuron in layer:
                    neuron.relations(prev_layer)
            else:
                for j, neuron in enumerate(layer):
                    neuron.relations([self.inputs[j]])

    def neurons(self):
        return itertools.chain(*self.layers)

    def apply(self, inputs):
        self.reset()
        self.data.set(inputs)
        return tuple([i.apply() for i in self.layers[-1]])

    def reset(self):
        for neuron in self.neurons():
            neuron.reset()

    def random(self, percentage=None):
        for neuron in self.neurons():
            neuron.random(percentage)
    

    def set_weights(self, value):
       for neuron in self.neurons():
            neuron.set_weights(value)

    def show(self):
        st = ''
        for index, layer in enumerate(self.layers):
            st += '\n\n\nLAYER %i\n' % index
            for j, neuron in enumerate(layer):
                st += '%.4i: %s\n' %(j, repr(neuron))
        return st


class Layer(list):
    pass


class Data(object):

    def __init__(self):
        self.data = list()

    def set(self, data):
        self.data = list(data)


    def get(self, index):
        return self.data[index]

