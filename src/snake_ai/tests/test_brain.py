import unittest
from snake_ai.brain import Brain


class ObjectsTestCase(unittest.TestCase):

    def test_1(self):
        brain = Brain([3, 2])
        self.assertSequenceEqual(brain.apply([1,1,1]), [0, 0])

        neuron = brain.layers[1][0]
        self.assertSequenceEqual(sorted(neuron.weights.keys(), key=lambda o: hash(o)), sorted(brain.layers[0], key=lambda o: hash(o)))

        brain.set_weights(0.5)
        self.assertSequenceEqual(brain.apply([1,1,1]), [0.6000182750981286, 0.6000182750981286])

