import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
from errors import FileNotCSVError, FileNotFoundError

"""
    utility class that loads the train data
    raises FileNotFoundError, FileNotCSVError
"""

class DataLoader:
    def __init__(self, data_file="data/train_data.csv"):
        if not os.path.exists(data_file):
            raise FileNotFoundError
        if data_file[-4:] != ".csv":
            raise FileNotCSVError

        # read data from csv file
        self.data = pd.read_csv(data_file, index_col=0)

        self.data = Data(self.data.drop(columns=['target', 'start']), self.data['target'])

        self.scaler = StandardScaler()
        self.scaler.fit(self.data.X)
        

    def get_data(self, scaled=True):
        if scaled:
            X = self.scaler.transform(self.data.X)
            return Data(X, self.data.y)
        else:
            return self.data

    def scale_data(self, data):
        return self.scaler.transform(data)


class Data:
    def __init__(self, X, y):
        self.X = X
        self.y = y
