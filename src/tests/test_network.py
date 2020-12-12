import unittest
from network import Network
from activation_functions import act_funcs
import random
from network import Layer, Unit


class TestNetwork(unittest.TestCase):

    def test_constructors(self):
        self.assertRaises(ValueError, Network, input_dim=-2, units_per_layer=[6, 2], acts=['relu', 'relu'])
        self.assertRaises(ValueError, Network, input_dim=2, units_per_layer=[-4, 1], acts=['relu', 'relu'])
        self.assertRaises(ValueError, Network, input_dim=3, units_per_layer=[3, 0], acts=['relu', 'relu'])
        self.assertRaises(ValueError, Network, input_dim=2, units_per_layer=[6, 2], acts=['relu', 'hello'])
        self.assertRaises(AttributeError, Network, input_dim=3, units_per_layer=[3, 2], acts=['relu', 'relu', 'relu'])
        self.assertRaises(ValueError, Layer,
                          [Unit(w=[0.5, 0.5, 0.5], b=1, act=act_funcs['sigmoid']),
                           Unit(w=[0.5, 0.5, 0.5], b=1, act=act_funcs['relu'])]
                          )

    def test_forward(self):
        net = Network(input_dim=3, units_per_layer=[6, 2], acts=['relu', 'relu'])
        self.assertRaises(AttributeError, net.forward, inp='hello')
        self.assertRaises(AttributeError, net.forward, inp=2)
        self.assertRaises(AttributeError, net.forward, inp=(1, 1))
        self.assertRaises(Exception, net.forward, inp=('a', 'b', 'c'))

    def test_compile(self):
        net = Network(input_dim=3, units_per_layer=[6, 2], acts=['relu', 'relu'])
        self.assertRaises(AttributeError, net.compile, opt='hello', loss='squared')
        self.assertRaises(AttributeError, net.compile, opt='sgd', loss='hello')

    def test_fit(self):
        net = Network(input_dim=3, units_per_layer=[6, 2], acts=['relu', 'relu'])
        self.assertRaises(AttributeError, net.fit, inp=[1, 1], target=[1, 2, 3])


if __name__ == '__main__':
    unittest.main()