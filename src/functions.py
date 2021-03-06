import math
import numpy as np


class Function:
    """
    Class representing a function
    Attributes:
        func (function "pointer"): Represents the function itself
        name (string): name of the function
    """

    def __init__(self, func, name):
        self.__func = func
        self.__name = name

    @property
    def name(self):
        return self.__name

    @property
    def func(self):
        return self.__func


class DerivableFunction(Function):
    """
    Class representing a function that we need the derivative of.
    Subclass of Function.
    Attributes:
        deriv (function "pointer"): Represents the derivative of the function
    """

    def __init__(self, func, deriv, name):
        super(DerivableFunction, self).__init__(func=func, name=name)
        self.__deriv = deriv

    @property
    def deriv(self):
        return self.__deriv


################################################
#            Activation Functions              #
################################################


def identity(x):
    """ identity (linear) activation function """
    return x


def identity_deriv(x):
    """ Computes the derivative of the identity function (i.e. 1) """
    return 1.


def relu(x):
    """ Computes the ReLU activation function """
    return np.maximum(x, 0)


def relu_deriv(x):
    """ Computes the derivative of the ReLU activation function """
    x[x <= 0] = 0
    x[x > 0] = 1
    return x


def leaky_relu(x):
    """ Computes the leaky ReLU activation function """
    return [i if i >= 0 else 0.01 * i for i in x]


def leaky_relu_deriv(x):
    """ Computes the derivative of the leaky ReLU activation function """
    x[x > 0] = 1.
    x[x <= 0] = 0.01
    return x


def sigmoid(x):
    """ Computes the sigmoid activation function """
    ones = [1.] * len(x)
    return np.divide(ones, np.add(ones, np.exp(-x)))


def sigmoid_deriv(x):
    """ Computes the derivative of the sigmoid activation function """
    return np.multiply(
        sigmoid(x),
        np.subtract([1.] * len(x), sigmoid(x))
    )


def tanh(x):
    """ Computes the hyperbolic tangent function (TanH) """
    return np.tanh(x)


def tanh_deriv(x):
    """ Computes the derivative of the hyperbolic tangent function (TanH) """
    return np.subtract(
        [1.] * len(x),
        np.power(np.tanh(x), 2)
    )


############################################
#            Loss Functions                #
############################################


def squared_loss(predicted, target):
    """
    Computes the squared error between the target vector and the output predicted by the net
    :param predicted: ndarray of shape (n, m) – Predictions for the n examples
    :param target: ndarray of shape (n, m) – Ground truth for each of n examples
    :return: loss in terms of squared error
    """
    return 0.5 * np.square(np.subtract(target, predicted))  # "0.5" is to make the gradient simpler


def squared_loss_deriv(predicted, target):
    """
    Computes the derivative of the squared error between the target vector and the output predicted by the net
    :param predicted: ndarray of shape (n, m) – Predictions for the n examples
    :param target: ndarray of shape (n, m) – Ground truth for each of n examples
    :return: derivative of the squared error
    """
    # exponent 2 in the deriv becomes a multiplying constant and simplifies itself with the denominator of the func
    return np.subtract(predicted, target)


############################################
#                Metrics                   #
############################################


def binary_class_accuracy(predicted, target):
    """
    Applies a threshold for computing classification accuracy (correct classification rate).
    If the difference in absolute value between predicted - target is less than a specified threshold it considers it
    correctly classified (returns 1). Else returns 0
    The threshold is 0.3
    """
    predicted = predicted[0]
    target = target[0]
    if np.abs(predicted - target) < 0.3:
        return [1]
    return [0]


def euclidean_loss(predicted, target):
    """
    Computes the euclidean error between the target vector and the output predicted by the net
    :param predicted: ndarray of shape (n, m) – Predictions for the n examples
    :param target: ndarray of shape (n, m) – Ground truth for each of n examples
    :return: error in terms of euclidean error
    """
    return np.linalg.norm(np.subtract(predicted, target))


#############################################
#         Learning rate schedules          #
#############################################


def linear_lr_decay(curr_lr, base_lr, final_lr, curr_step, limit_step, **kwargs):
    """
    The linear_lr_decay, linearly decays the learning rate (base_lr) by a decay_rate until iteration "limit_step".
    Then it stops decaying and uses a fix learning rate (final_lr):
    :param curr_lr: current learning (decayed)
    :param base_lr: initial learning rate
    :param final_lr: final (fixed) learning rate
    :param curr_step: current iteration
    :param limit_step: corresponds to the number of step when the learning rate will stop decaying
    :return: updated (decayed) learning rate
    """
    if curr_step < limit_step and curr_lr > final_lr:
        decay_rate = curr_step / limit_step
        curr_lr = (1. - decay_rate) * base_lr + decay_rate * final_lr
        return curr_lr
    return final_lr


def exp_lr_decay(base_lr, decay_rate, curr_step, decay_steps, staircase=False, **kwargs):
    """
    The exp_lr_decay, decays exponentially the learning rate by `decay_rate` every `decay_steps`,
    starting from a `base_lr`
    :param base_lr: The learning rate at the first step
    :param decay_rate: The amount to decay the learning rate at each new stage
    :param decay_steps: The length of each stage, in steps
    :param staircase: If True, only adjusts the learning rate at the stage transitions, producing a step-like decay
    schedule. If False, adjusts the learning rate after each step, creating a smooth decay schedule. Default is True
    :return: updated (decayed) learning rate
    """
    cur_stage = curr_step / decay_steps
    if staircase:
        cur_stage = np.floor(cur_stage)
    decay = -decay_rate * cur_stage
    return base_lr * math.exp(decay)


###########################################
#            Regularizations              #
###########################################


def lasso_l1(w, lambd):
    """
    Computes Lasso regularization (L1) on the nets' weights
    :param w: (list of matrices) the list of each layer's weights
    :param lambd: (float) regularization coefficient
    """
    return lambd * np.sum(np.abs(w))


def lasso_l1_deriv(w, lambd):
    """
    Computes the derivative of the Lasso regularization (L1)
    :param w: (list of matrices) the list of each layer's weights
    :param lambd: (float) regularization coefficient
    """
    res = np.zeros(w.shape)
    for i in range(w.shape[0]):
        for j in range(w.shape[1]):
            if w[i][j] < 0:
                res[i][j] = -lambd
            elif w[i][j] > 0:
                res[i][j] = lambd
            else:
                res[i][j] = 0
    return res


def ridge_l2(w, lambd):
    """
    Computes Tikhonov regularization (L2) on the nets' weights
    :param w: (list of matrices) the list of each layer's weights
    :param lambd: (float) regularization coefficient
    """
    return lambd * np.sum(np.square(w))


def ridge_l2_deriv(w, lambd):
    """
    Computes the derivative of Tikhonov regularization (L1)
    :param w: (list of matrices) the list of each layer's weights
    :param lambd: (float) regularization coefficient
    """
    return 2 * lambd * w


###########################################################################
#     Function objects and dictionaries (used in other scripts)           #
###########################################################################

# activation functions
Identity = DerivableFunction(identity, identity_deriv, 'identity')
ReLU = DerivableFunction(relu, relu_deriv, 'ReLU')
LeakyReLU = DerivableFunction(leaky_relu, leaky_relu_deriv, 'LeakyReLU')
Sigmoid = DerivableFunction(sigmoid, sigmoid_deriv, 'Sigmoid')
Tanh = DerivableFunction(tanh, tanh_deriv, 'Tanh')
act_funcs = {
    'identity': Identity,
    'relu': ReLU,
    'leaky_relu': LeakyReLU,
    'sigmoid': Sigmoid,
    'tanh': Tanh,
}

# losses
SquaredLoss = DerivableFunction(squared_loss, squared_loss_deriv, 'squared')
losses = {
    'squared': SquaredLoss,
}

# metrics
BinClassAcc = Function(binary_class_accuracy, 'bin_class_acc')
Euclidean = Function(euclidean_loss, 'euclidean')
metrics = {
    'bin_class_acc': BinClassAcc,
    'euclidean': Euclidean
}

# learning rate schedulers
LinearLRDecay = Function(linear_lr_decay, 'linear')
ExponentialLRDecay = Function(exp_lr_decay, 'exponential')

lr_decays = {
    'linear': LinearLRDecay,
    'exponential': ExponentialLRDecay
}

# regularizations
l2_regularization = DerivableFunction(ridge_l2, ridge_l2_deriv, 'l2')
l1_regularization = DerivableFunction(lasso_l1, lasso_l1_deriv, 'l1')
regs = {
    'l2': l2_regularization,
    'l1': l1_regularization
}
