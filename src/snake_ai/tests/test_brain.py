import unittest
from snake_ai.brain import Brain
from snake_ai.brain import TanHNeuron

class ObjectsTestCase(unittest.TestCase):

    def test_1(self):
        a = Brain([3,2])
        b = Brain([3,2])

        a.set_weights(1)
        b.set_weights(2)

        ca, cb = Brain.crossover(a, b, 1)
        self.assertSequenceEqual(list(ca.layers[1][0].weights.values()), [2,2,2,2])
        self.assertSequenceEqual(list(ca.layers[1][1].weights.values()), [1,1,1,2])
        self.assertSequenceEqual(list(cb.layers[1][0].weights.values()), [1,1,1,1])
        self.assertSequenceEqual(list(cb.layers[1][1].weights.values()), [2,2,2,1])


        ca, cb = Brain.crossover(a, b, 2)
        self.assertSequenceEqual(list(ca.layers[1][0].weights.values()), [1,2,2,2])
        self.assertSequenceEqual(list(ca.layers[1][1].weights.values()), [1,1,1,1])
        self.assertSequenceEqual(list(cb.layers[1][0].weights.values()), [2,1,1,1])
        self.assertSequenceEqual(list(cb.layers[1][1].weights.values()), [2,2,2,2])


    def test_2(self):
        brain = Brain([3, 2], TanHNeuron)
        brain.set_weights(0)
        self.assertSequenceEqual(brain.apply([1,1,1]), [0, 0])

        neuron = brain.layers[1][0]
        self.assertSequenceEqual(sorted(neuron.weights.keys(), key=lambda o: hash(o)), sorted(brain.layers[0], key=lambda o: hash(o)))

        brain.set_weights(0.5)
        self.assertSequenceEqual(brain.apply([1,1,1]), [0.8315611928975513, 0.8315611928975513])

