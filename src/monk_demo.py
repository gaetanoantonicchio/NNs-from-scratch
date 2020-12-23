import pandas as pd
import numpy as np
from network.network import Network
from sklearn.preprocessing import OneHotEncoder

if __name__ == '__main__':
    # read the dataset
    col_names = ['class', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'Id']
    monk1_train = pd.read_csv("../datasets/monks/monks-1.train", sep=' ', names=col_names)
    monk1_train.set_index('Id', inplace=True)
    labels = monk1_train.pop('class')

    # 1-hot encoding (and transform dataframe to numpy array)
    monk1_train = OneHotEncoder().fit_transform(monk1_train).toarray()

    # transform labels from pandas dataframe to numpy ndarray
    labels = labels.to_numpy()[:, np.newaxis]

    parameters = {
        'input_dim': 17,
        'units_per_layer': (3, 1),
        'acts': ('relu', 'sigmoid'),
        'init_type': 'random',
        'weights_value': 0.2,
        'lower_lim': 10,
        'upper_lim': 12
    }
    model = Network(**parameters)
    model.print_net()
    model.compile(opt='gd', loss='squared', metr='bin_class_acc', lrn_rate=0.8)
    model.fit(inputs=monk1_train, targets=labels, epochs=10, batch_size=len(monk1_train))
