import numpy as np
from Function import Function


def mean_squared_error(predicted, target):
    """
    Computes the mean squared error between
    the target vector and the output predicted by the net

    :param predicted: ndarray of shape (n, m) – Predictions for the n examples
    :param target: ndarray of shape (n, m) – Ground truth values for each of n examples
    :return: loss in terms of mse (Mean Squared Error)
    """
    # Check shapes
    predicted = np.array(predicted)
    target = np.array(target)
    if predicted.shape != target.shape:
        raise Exception(f"Mismatching shapes in MSE: predictions shape: "
                        f"{predicted.shape} - targets shape {target.shape}")

    return np.sum(np.square(predicted - target)) / (target.shape[0] * 2)    # "* 2" is to make the gradient simpler


def mean_squared_error_deriv(predicted, target):
    """
    Computes the derivative of the mean squared error between
    the target vector and the output predicted by the net

    :param predicted: ndarray of shape (n, m) – Predictions for the n examples
    :param target: ndarray of shape (n, m) – Ground truth values for each of n examples
    :return: derivative of the mse (Mean Squared Error)
    """
    return 2 * np.sum(predicted - target) / target.shape[0]




def mean_euclidean_error(predicted, target):
    """
    Computes the Mean Euclidean Error between
    the target vector and the output predicted by the net

    :param predicted: ndarray of shape (n, m) – Predictions for the n examples
    :param target: ndarray of shape (n, m) – Ground truth values for each of n examples
    :return: loss in term of mee (Mean Euclidean Error)
    """
    return np.linalg.norm(predicted - target) / target.shape[0]


def mean_euclidean_error_deriv(predicted, target):
    """
    Computes the derivative of the Mean Euclidean Error between
    the target vector and the output predicted by the net

    :param predicted: ndarray of shape (n, m) – Predictions for the n examples
    :param target: ndarray of shape (n, m) – Ground truth values for each of n examples
    :return: derivative of the mee (Mean Euclidean Error)
    """
    # TODO: check!!!
    return (predicted - target) / np.linalg.norm(predicted - target)


MSE = Function(mean_squared_error, mean_squared_error_deriv, 'mse')
MEE = Function(mean_euclidean_error, mean_euclidean_error_deriv, 'mee')

losses = {
    'mse': MSE,
    'mee': MEE
}

if __name__ == '__main__':
    # Test loss functions
    print('\nArrays for testing loss functions:')
    y_true = np.array(
        [[1, 1, 0, 0],
         [0, 0, 0, 0]]
    )
    y_pred = np.array(
        [[1, 0, 0, 1],
         [1, 1, 1, 1]]
    )

    print(f"target:\n{y_true}")
    print(f"predicted:\n{y_pred}\n")
    print('Loss functions test:')
    print(f"MSE:{mean_squared_error(y_pred, y_true)}")
    # print(f"MSE_deriv:{mean_squared_error_deriv(y_true, y_pred)}")
    print(f"MEE:{mean_euclidean_error(y_true, y_pred)}")
    # print(f"MEE_deriv:{mean_euclidean_error_deriv(y_true, y_pred)}")
