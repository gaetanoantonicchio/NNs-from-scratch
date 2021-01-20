import json
import numpy as np
from joblib import Parallel, delayed
import os
from network import Network
from utility import read_cup


class Ensembler:
    def __init__(self, models_filenames: list, retrain: bool):
        self.models = []
        for filename in models_filenames:
            with open(filename, 'r') as f:
                models_data = json.load(f)

            self.models.append({
                'model': Network(**models_data['model_params']),
                'model_params': models_data['model_params'],
                'train_params': models_data['train_params']
            })

            if not retrain:
                # reshape weights
                for i in range(len(models_data['weights'])):
                    models_data['weights'][i] = np.array(
                        np.reshape(models_data['weights'][i], newshape=np.shape(models_data['weights'][i])))
                    self.models[-1]['model'].weights = models_data['weights']

    def compile(self):
        for model in self.models:
            model['model'].compile(**model['train_params'])

    def fit(self):
        tr_x, tr_y, _ = read_cup()
        for model in self.models:
            model['model'].fit(tr_x=tr_x, tr_y=tr_y, disable_tqdm=False, **model['train_params'])

    def fit_parallel(self):
        Parallel(n_jobs=os.cpu_count())(delayed(m['model'].fit) for m in self.models)