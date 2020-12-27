import unittest
import numpy as np
from functions import act_funcs, regs, losses, metrics


class TestFunctions(unittest.TestCase):
    def test_act_funcs(self):
        self.assertAlmostEqual(act_funcs['sigmoid'].func(1.), 0.7310585786300049)
        self.assertEqual(act_funcs['relu'].func(2.), 2.)
        self.assertEqual(act_funcs['relu'].func(-3.), 0.)
        self.assertAlmostEqual(act_funcs['tanh'].func(1.), 0.7615941559557649)
        self.assertEqual(act_funcs['relu'].func([[[2.]]]), 2.)
        self.assertEqual(act_funcs['leaky_relu'].func(1.), 1.)
        self.assertEqual(act_funcs['leaky_relu'].func(-1.), -0.01)
        # test activation functions' derivatives
        self.assertAlmostEqual(act_funcs['sigmoid'].deriv(1.), 0.19661193324148185)
        self.assertEqual(act_funcs['relu'].deriv(2.), 1.)
        self.assertEqual(act_funcs['relu'].deriv(-3.), 0.)
        self.assertAlmostEqual(act_funcs['tanh'].deriv(1.), 0.41997434161402614)
        self.assertEqual(act_funcs['leaky_relu'].deriv(1.), 1.)
        self.assertEqual(act_funcs['leaky_relu'].deriv(-1.), 0.01)

    def test_losses(self):
        predicted = [1, 0, 0, 1]
        target = [1, 1, 0, 0]
        ground_truth = [0., 0.5, 0., 0.5]
        for i in range(len(ground_truth)):
            self.assertEqual(
                losses['squared'].func(predicted, target)[i],
                ground_truth[i]
            )
        ground_truth = [0., -1., 0., 1.]
        for i in range(len(ground_truth)):
            self.assertEqual(
                losses['squared'].deriv(predicted, target)[i],
                ground_truth[i]
            )

    def test_regularizations(self):
        lambd = 0.2
        w = np.array([[1, 0.2, -1], [1, 0, 0.5]])
        l1_deriv = np.array([[1, 1, -1], [1, 0, 1]]) * lambd
        l2_deriv = np.array([[0.4, 0.08, -0.4], [0.4, 0., 0.2]])
        self.assertAlmostEqual(regs['l1'].func(w, lambd=lambd), 0.740000)
        self.assertAlmostEqual(regs['l2'].func(w, lambd=lambd), 0.658)
        np.testing.assert_array_almost_equal(regs['l1'].deriv(w, lambd=lambd), l1_deriv)
        np.testing.assert_array_almost_equal(regs['l2'].deriv(w, lambd=lambd), l2_deriv)

    def test_metrics(self):
        predicted = np.array(
            [[1, 0, 0, 1],
             [1, 1, 1, 1]]
        )
        target = np.array(
            [[1, 1, 0, 0],
             [0, 0, 0, 0]]
        )
        acc = np.array([0])
        predicted = np.array([[0], [1], [1], [0.8]])
        target = np.array([[1], [1], [1], [1]])
        for i in range(len(predicted)):
            acc += metrics['bin_class_acc'].func(predicted[i], target[i])
        self.assertEqual(3, acc)
        acc = acc / float(len(predicted))
        self.assertEqual(0.75, acc)

    def test_exceptions(self):
        # check many combination
        # it may be enough to test the function 'check_is_number', but this way we check also that
        # we call 'check_is_number' in every activation function and deriv
        activation = ['sigmoid', 'relu', 'leaky_relu', 'tanh']
        attribute_test = [[1, [1, 2, 3]], 'hello']
        for act in activation:
            for attr_test in attribute_test:
                self.assertRaises(AttributeError, act_funcs[act].func, attr_test)
                self.assertRaises(AttributeError, act_funcs[act].deriv, attr_test)
        self.assertRaises(Exception, losses['squared'].func, [0, 0], [0, 0, 0])
        self.assertRaises(Exception, losses['squared'].deriv, [0, 0], [0, 0, 0])
        # self.assertRaises(KeyError, regularization['nonexistent_reg'].func, self.w, lambd=0.1)
        # self.assertRaises(ValueError, regularization['l1'].func, self.w, lambd=-0.5)


if __name__ == '__main__':
    unittest.main()
