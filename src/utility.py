import numpy as np
import pandas as pd
import os
import math
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from collections import OrderedDict
import random
import itertools as it
import json
from network import Network


def read_monk(name, rescale=False):
    """
    Reads the monks datasets
    :param name: name of the dataset
    :param rescale: whether or not to rescale the targets to [-1, +1]
    :return: monk dataset and labels (as numpy ndarrays)
    """
    # read the dataset
    col_names = ['class', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'Id']
    monk_dataset = pd.read_csv(f"../datasets/monks/{str(name)}", sep=' ', names=col_names)
    monk_dataset.set_index('Id', inplace=True)
    labels = monk_dataset.pop('class')

    # 1-hot encoding (and transform dataframe to numpy array)
    monk_dataset = OneHotEncoder().fit_transform(monk_dataset).toarray().astype(np.float32)

    # transform labels from pandas dataframe to numpy ndarray
    labels = labels.to_numpy()[:, np.newaxis]
    if rescale:
        labels[labels == 0] = -1

    # shuffle the whole dataset once
    indexes = list(range(len(monk_dataset)))
    np.random.shuffle(indexes)
    monk_dataset = monk_dataset[indexes]
    labels = labels[indexes]

    return monk_dataset, labels


def read_cup(int_ts=False):
    """
    Reads the CUP training and test set
    :return: CUP training data, CUP training targets and CUP test data (as numpy ndarray)
    """
    # read the dataset
    col_names = ['id', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'target_x', 'target_y']
    directory = "../datasets/cup/"
    int_ts_path = directory + "CUP-INTERNAL-TEST.csv"
    dev_set_path = directory + "CUP-DEV-SET.csv"
    file = "ML-CUP20-TR.csv"

    if int_ts and not (os.path.exists(int_ts_path) and os.path.exists(dev_set_path)):
        df = pd.read_csv(directory + file, sep=',', names=col_names, skiprows=range(7), usecols=range(0, 13))
        df = df.sample(frac=1, axis=0)
        int_ts_df = df.iloc[: math.floor(len(df) * 0.1), :]
        dev_set_df = df.iloc[math.floor(len(df) * 0.1) :, :]
        int_ts_df.to_csv(path_or_buf=int_ts_path, index=False, float_format='%.6f', header=False)
        dev_set_df.to_csv(path_or_buf=dev_set_path, index=False, float_format='%.6f', header=False)

    if int_ts and os.path.exists(int_ts_path) and os.path.exists(dev_set_path):
        tr_data = pd.read_csv(dev_set_path, sep=',', names=col_names, skiprows=range(7), usecols=range(1, 11))
        tr_targets = pd.read_csv(dev_set_path, sep=',', names=col_names, skiprows=range(7), usecols=range(11, 13))
        int_ts_data = pd.read_csv(int_ts_path,  sep=',', names=col_names, skiprows=range(7), usecols=range(1, 11))
        int_ts_targets = pd.read_csv(int_ts_path,  sep=',', names=col_names, skiprows=range(7), usecols=range(11, 13))
        int_ts_data = int_ts_data.to_numpy(dtype=np.float32)
        int_ts_targets = int_ts_targets.to_numpy(dtype=np.float32)
    else:
        tr_data = pd.read_csv(directory + file, sep=',', names=col_names, skiprows=range(7), usecols=range(1, 11))
        tr_targets = pd.read_csv(directory + file, sep=',', names=col_names, skiprows=range(7), usecols=range(11, 13))

    file = "ML-CUP20-TS.csv"
    cup_ts_data = pd.read_csv(directory + file, sep=',', names=col_names[: -2], skiprows=range(7), usecols=range(1, 11))

    tr_data = tr_data.to_numpy(dtype=np.float32)
    tr_targets = tr_targets.to_numpy(dtype=np.float32)
    cup_ts_data = cup_ts_data.to_numpy(dtype=np.float32)

    # shuffle the training dataset once
    indexes = list(range(tr_targets.shape[0]))
    np.random.shuffle(indexes)
    tr_data = tr_data[indexes]
    tr_targets = tr_targets[indexes]

    # detach internal test set if needed
    if int_ts:
        if not (os.path.exists(int_ts_path) and os.path.exists(dev_set_path)):
            tr_data, int_ts_data, tr_targets, int_ts_targets = train_test_split(tr_data, tr_targets, test_size=0.1)

        return tr_data, tr_targets, int_ts_data, int_ts_targets, cup_ts_data

    return tr_data, tr_targets, cup_ts_data


def sets_from_folds(x_folds, y_folds, val_fold_index):
    """
    Takes folds from cross validation and return training and validation sets as a whole (not lists of folds)
    :param x_folds: list of folds containing the data
    :param y_folds: list of folds containing the targets
    :param val_fold_index: index of the fold to use as validation set
    :return: training data set, training targets set, validation data set, validation targets set (as numpy ndarray)
    """
    val_data, val_targets = x_folds[val_fold_index], y_folds[val_fold_index]
    tr_data_folds = np.concatenate((x_folds[: val_fold_index], x_folds[val_fold_index + 1:]))
    tr_targets_folds = np.concatenate((y_folds[: val_fold_index], y_folds[val_fold_index + 1:]))
    # here tr_data_folds & tr_targets_folds are still a "list of folds", we need a single seq as a whole
    tr_data = tr_data_folds[0]
    tr_targets = tr_targets_folds[0]
    for j in range(1, len(tr_data_folds)):
        tr_data = np.concatenate((tr_data, tr_data_folds[j]))
        tr_targets = np.concatenate((tr_targets, tr_targets_folds[j]))
    tr_data = np.array(tr_data, dtype=np.float32)
    tr_targets = np.array(tr_targets, dtype=np.float32)
    val_data = np.array(val_data, dtype=np.float32)
    val_targets = np.array(val_targets, dtype=np.float32)
    return tr_data, tr_targets, val_data, val_targets


def randomize_params(base_params, fb_dim, n_config=2):
    """
    Generates combination of random hyperparameters
    :param base_params: parameters on which the random perturbation will be applied
    :param fb_dim: full batch dimension (expressed as a number)
    :param n_config: number of random configurations to be generated for each hyper-parameter
    :return: combos of randomly generated hyper-parameters' values
    """
    n_config -= 1
    rand_params = {}
    for k, v in base_params.items():
        # if the parameter does not have to change
        if k in ('acts', 'init_type', 'decay_rate', 'loss', 'lr_decay', 'metr', 'reg_type', 'staircase',
                 'units_per_layer', 'limits', 'epochs'):
            rand_params[k] = (v,)
        else:
            rand_params[k] = [v]
            for i in range(n_config):
                # generate n_config random value centered in v
                if k == "batch_size":
                    if v == "full":
                        rand_params[k] = ("full",)
                        continue
                    lower = max(v - 15, 1)
                    upper = min(v + 15, fb_dim)
                    value = random.randint(lower, upper)
                    for bs in rand_params[k]:
                        if abs(value - bs) < 5:
                            value = rand_params[k][0]
                    while value in rand_params[k]:
                        lower = max(v - 15, 1)
                        upper = min(v + 15, fb_dim)
                        value = random.randint(lower, upper)
                        for bs in rand_params[k]:
                            if abs(value - bs) < 5:
                                value = rand_params[k][0]
                    rand_params[k].append(value)

                # elif k == "decay_rate":
                #     if v is not None:
                #         lower = max(0., v - 0.2)
                #         upper = min(1., v + 0.2)
                #         rand_params[k].append(random.uniform(lower, upper))
                #     else:
                #         rand_params[k] = (None,)

                elif k in ("limit_step", "decay_steps"):
                    if base_params['lr_decay'] is not None:
                        if v is None or (base_params['lr_decay'] == 'linear' and k == 'decay_steps') or \
                                (base_params['lr_decay'] == 'exponential' and k == 'limit_step'):
                            rand_params[k] = (None,)
                            continue
                        lower = max(1, v - 100)
                        upper = v + 100
                        rand_params[k].append(random.randint(lower, upper))
                    else:
                        rand_params[k] = (v,)

                elif k in ("lambd", "lr"):
                    value = max(0., np.random.normal(loc=v, scale=0.001))
                    for l in rand_params[k]:
                        if abs(value - l) < 0.0005:
                            value = rand_params[k][0]
                    while value in rand_params[k]:
                        value = max(0., np.random.normal(loc=v, scale=0.001))
                        for l in rand_params[k]:
                            if abs(value - l) < 0.0005:
                                value = rand_params[k][0]
                    rand_params[k].append(value)

                # elif k == "limits":
                #     lower, upper = v[0], v[1]
                #     lower = np.random.normal(loc=lower, scale=0.1)
                #     upper = np.random.normal(loc=upper, scale=0.1)
                #     if lower > upper:
                #         aux = lower
                #         lower = upper
                #         upper = aux
                #     rand_params[k].append((lower, upper))

                elif k == "momentum":
                    value = max(0., np.random.normal(loc=v, scale=0.1))
                    for m in rand_params[k]:
                        if abs(value - m) < 0.05:
                            value = rand_params[k][0]
                    while value in rand_params[k] or value > 1.:
                        value = min(1., np.random.normal(loc=v, scale=0.1))
                        for m in rand_params[k]:
                            if abs(value - m) < 0.05:
                                value = rand_params[k][0]
                    rand_params[k].append(value)

    print(rand_params)
    return rand_params


def list_of_combos(param_dict):
    """
    Takes a dictionary with the combinations of params to use in the grid search and creates a list of dictionaries, one
    for each combination (so it's possible to iterate over this list in the GS, instead of having many nested loops)
    :param param_dict: dict{kind_of_param: tuple of all the values of that param to try in the grid search)
    :return: list of dictionaries{kind_of_param: value of that param}
    """
    expected_keys = sorted(['units_per_layer', 'acts', 'init_type', 'limits', 'momentum', 'batch_size', 'lr', 'loss',
                            'metr', 'epochs', 'lr_decay', 'decay_rate', 'decay_steps', 'staircase', 'limit_step',
                            'lambd', 'reg_type'])
    for k in expected_keys:
        if k not in param_dict.keys():
            param_dict[k] = ('l2',) if k == 'reg_type' else ((0,) if k == 'lambd' else (None,))
    param_dict = OrderedDict(sorted(param_dict.items()))
    combo_list = list(it.product(*(param_dict[k] for k in param_dict.keys())))
    combos = []
    for c in combo_list:
        if len(c[expected_keys.index('units_per_layer')]) == len(c[expected_keys.index('acts')]):
            d = {k: c[i] for k, i in zip(expected_keys, range(len(expected_keys)))}
            combos.append(d)

    for c in combos:
        if c['lr_decay'] == 'linear':
            c['decay_rate'] = None
            c['decay_steps'] = None
            c['staircase'] = False
        elif c['lr_decay'] == 'exponential':
            c['limit_step'] = None

    final_combos = []
    for i in range(len(combos) - 1):
        if combos[i] != combos[i + 1]:
            final_combos.append(combos[i])

    return final_combos


def get_best_models(dataset, coarse=False, n_models=1, fn=None):
    """
    Search and select the best models based on the MEE metric and standard deviation
    :param dataset: name of the dataset (used for reading the file containing the results)
    :param coarse: indicates if best models result from a coarse or fine grid search (used for reading the file name)
    :param n_models: number of best models to be returned
    :param fn: file name for reading a specific file for the results (if different from the default)
    :return: best models in term of MEE and standard deviation and their parameters
    """
    file_name = ("coarse_gs_" if coarse else "fine_gs_") + "results_" + dataset + ".json"
    file_name = file_name if fn is None else fn
    with open("../results/" + file_name, 'r') as f:
        data = json.load(f)

    # put the data into apposite lists
    input_dim = 10 if dataset == "cup" else 17
    models, params, errors, std_errors, metrics, std_metrics = [], [], [], [], [], []
    for result in data['results']:
        if result is not None:
            errors.append(round(result[0], 3))
            std_errors.append(round(result[1], 3))
            metrics.append(round(result[2], 3))
            std_metrics.append(round(result[3], 3))

    errors, std_errors = np.array(errors), np.array(std_errors)
    metrics, std_metrics = np.array(metrics), np.array(std_metrics)
    for i in range(n_models):
        # find best metric model and its index
        index_of_best = np.argmin(metrics) if dataset == "cup" else np.argmax(metrics)
        value_of_best = min(metrics) if dataset == "cup" else max(metrics)

        # search elements with the same value
        if len(metrics) > index_of_best + 1:
            indexes = [index_of_best]
            for j in range(index_of_best + 1, len(metrics)):
                if metrics[j] == value_of_best:
                    indexes.append(j)

            std_metr_to_check = std_metrics[indexes]
            value_of_best = min(std_metr_to_check)
            index_of_best = indexes[np.argmin(std_metr_to_check)]
            for j in indexes:
                if std_metrics[j] != value_of_best:
                    indexes.remove(j)

            err_to_check = errors[indexes]
            value_of_best = min(err_to_check)
            index_of_best = indexes[np.argmin(err_to_check)]
            for j in indexes:
                if errors[j] != value_of_best:
                    indexes.remove(j)

            std_err_to_check = std_errors[indexes]
            value_of_best = min(std_err_to_check)
            index_of_best = indexes[np.argmin(std_err_to_check)]
            for j in indexes:
                if std_errors[j] != value_of_best:
                    indexes.remove(j)

        metrics = np.delete(metrics, index_of_best)
        models.append(Network(input_dim=input_dim, **data['params'][index_of_best]))
        params.append(data['params'][index_of_best])

    return models, params


def plot_curves(tr_loss, val_loss, tr_metr, val_metr, path=None, ylim=(0., 10.), lbltr='development',
                lblval='internal test', *args):
    """
    Plot the curves of training loss, training metric, validation loss, validation metric
    :param tr_loss: vector with the training error values
    :param val_loss: vector with the validation error values
    :param tr_metr: vector with the training metric values
    :param val_metr: vector with the validation metric values
    :param path: if not None, path where to save the plot (otherwise it will be displayed)
    :param ylim: value for "set_ylim" of pyplot
    :param lbltr: label for the training curve
    :param lblval: label for the validation curve
    """
    figure, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(range(len(tr_loss)), tr_loss, color='b', linestyle='dashed', label=lbltr)
    ax[0].plot(range(len(val_loss)), val_loss, color='r', label=lblval)
    ax[0].legend(loc='best', prop={'size': 9})
    ax[0].set_xlabel('Epochs', fontweight='bold')
    ax[0].set_ylabel('Error', fontweight='bold')
    ax[0].grid()
    ax[1].plot(range(len(tr_metr)), tr_metr, color='b', linestyle='dashed', label=lbltr)
    ax[1].plot(range(len(val_metr)), val_metr, color='r', label=lblval)
    ax[1].legend(loc='best', prop={'size': 9})
    ax[1].set_xlabel('Epochs', fontweight='bold')
    ax[1].set_ylabel('Metric', fontweight='bold')
    ax[1].set_ylim(ylim)
    ax[1].grid()
    if path is None:
        plt.show()
    else:
        plt.savefig(path)
