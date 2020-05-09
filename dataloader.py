import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os
from errors import FileNotCSVError, FileNotFoundError

"""
    utility class that loads the train data
    raises FileNotFoundError, FileNotCSVError
"""

class DataLoader:
    def __init__(self, data_file="data/prepared_train_data.csv", test_data="data/test_data_denoised_n_f.csv",
                    sample_submission="data/sample_submission.csv"):
        if not os.path.exists(data_file):
            raise FileNotFoundError
        if data_file[-4:] != ".csv":
            raise FileNotCSVError

        # read data from csv file
        self.data = pd.read_csv(data_file, index_col=0, sep=',', dtype=np.float32)

        self.data = Data(self.data.drop(columns=['target']), self.data['target'])

        self.scaler = StandardScaler()
        self.scaler.fit(self.data.X)

        # load test data
        if not os.path.exists(test_data):
            raise FileNotFoundError

        self.test_data = pd.read_csv(test_data, index_col=0, header=0)

        # load sample submission data
        if not os.path.exists(sample_submission):
            raise FileNotFoundError
        self.sample_file = pd.read_csv(sample_submission, index_col=0)

    def get_data(self, scaled=True):
        if scaled:
            X = self.scaler.transform(self.data.X)
            return Data(pd.DataFrame(X), self.data.y)
        else:
            return self.data

    def scale_data(self, data):
        return self.scaler.transform(data)

    def get_test_data(self, scaled=True):
        if scaled:
            return pd.DataFrame(self.scaler.transform(self.test_data))
        else:
            return self.test_data

    def get_sample_file(self):
        return self.sample_file


class Data:
    def __init__(self, X, y):
        self.X = X
        self.y = y
