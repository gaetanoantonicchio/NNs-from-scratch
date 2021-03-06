import unittest
from weights_initializations import weights_inits


class TestWeightsInitializations(unittest.TestCase):
    def test_exceptions(self):
        self.assertRaises(TypeError, weights_inits, foo='foo')
        self.assertRaises(TypeError, weights_inits)
        self.assertRaises(KeyError, weights_inits, 'fake_type')
        self.assertRaises(TypeError, weights_inits, init_type='fixed')
        self.assertRaises(TypeError, weights_inits, init_type='uniform')
        self.assertRaises(TypeError, weights_inits, init_type='uniform', n_weights=2, upper_lim=-0.2, lower_lim=0.)

    def test_values(self):
        value = 0.2
        self.assertEqual(weights_inits(init_type='fixed', init_value=value, n_weights=1, n_units=1), value)
        self.assertLessEqual(weights_inits(init_type='uniform', limits=(0., value), n_weights=1, n_units=1), value)
        self.assertGreaterEqual(weights_inits(init_type='uniform', limits=(value, value+1), n_weights=1, n_units=1), value)


if __name__ == '__main__':
    unittest.main()
