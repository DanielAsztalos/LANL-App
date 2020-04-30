from dataloader import DataLoader
from paramloader import ParamLoader
from models import get_model

from sklearn.model_selection import RandomizedSearchCV, train_test_split, KFold
from sklearn.metrics import mean_absolute_error

import threading
import time
import numpy as np
from datetime import datetime
import os


# This class handles the Random Parameter Search functionality
class SearchParams:
    def __init__(self, model, grid, queue, name):
        dataloader = DataLoader()
        self.data = dataloader.get_data()
        self.model = model
        self.grid = grid
        self.queue = queue
        self.name = name

    def execute(self):
        # instantiate random search with the given parameters and fit
        src = RandomizedSearchCV(self.model, self.grid, n_iter=50, cv=3, scoring='neg_mean_absolute_error')
        src.fit(self.data.X, self.data.y)

        # when done send a signal to the checker process
        self.queue.put("Done")

        # send results
        params = dict()
        params[self.name] = src.best_params_
        self.queue.put(params)

# this class when running on a different thread checks continuously if a given
# thread is still alive, and refreshes the status bar accordingly
class CheckSearch:
    def __init__(self, process, queue, shared, after):
        self.process = process
        self.queue = queue
        self.shared = shared
        self.after = after

    def execute(self):

        while True:
            
            if not self.queue.empty():

                # if queue is not empty check if the first element in the query is the 
                # "Done" signal, if yes, then exit else ignore it

                elem = self.queue.get()
                if elem == "Done":
                    self.shared.state_lock.acquire()
                    self.shared.state.set("Task finished")
                    self.shared.state_lock.release()

                    self.after(self.queue)
            
                    return
            else:
                # add dots to the status of the app to signal that it is still 
                # executing the task

                self.shared.state_lock.acquire()
                state = self.shared.state.get()
                if len(state) > 3 and state[-1] =='.' and state[-2] == '.' and state[-3] == '.':
                    self.shared.state.set(state[:-3])
                else:
                    self.shared.state.set(self.shared.state.get() + ".")
                self.shared.state_lock.release()

            # if process is finished exit
            if not self.process.isAlive(): 
                self.shared.state_lock.acquire()
                self.shared.state.set("Task finished")
                self.shared.state_lock.release()

                return

            time.sleep(1)

# this class realises the training and testing of a given model
class TrainAndTest:
    def __init__(self, shared, queue, n_folds, test_size, upload_to_kaggle):
        self.shared = shared
        self.queue = queue
        self.n_folds = n_folds
        self.test_size = test_size
        self.upload_to_kaggle = upload_to_kaggle

    def execute(self):
        # load data
        data_loader = DataLoader()
        data = data_loader.get_data()

        # split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(data.X, data.y, test_size=self.test_size)

        # get ml model
        model = get_model(self.shared.selected_model)
        model.set_params(**self.shared.param_grid)

        # initialize folds
        folds = KFold(n_splits=self.n_folds)

        train_scores = []
        test_scores = []
        kaggle_pred = np.zeros((data_loader.get_test_data().shape[0],))

        # reset indexes in the train data
        X_train = X_train.reset_index()
        X_train = X_train.drop('index', axis=1)
        y_train = y_train.reset_index()
        y_train = y_train.drop('index', axis=1)

        # train model
        for fold, (train_idx, test_idx) in enumerate(folds.split(X_train, y_train)):
            self.shared.state_lock.acquire()
            self.shared.state.set("Train fold: {}/{}".format(fold+1, self.n_folds))
            self.shared.state_lock.release()

            x_tr, x_te = X_train.loc[train_idx], X_train.loc[test_idx]
            y_tr, y_te = y_train.loc[train_idx], y_train.loc[test_idx]

            model.fit(x_tr, y_tr)

            train_scores.append(mean_absolute_error(y_te, model.predict(x_te)))
            test_scores.append(mean_absolute_error(y_test, model.predict(X_test)))

            if self.upload_to_kaggle:
                kaggle_pred += model.predict(data_loader.get_test_data())

        self.shared.model_lock.acquire()
        self.shared.model = model
        self.shared.model_lock.release()

        if self.upload_to_kaggle:
            self.shared.state_lock.acquire()
            self.shared.state.set("Submiting to kaggle...")
            self.shared.state_lock.release()

            sample = data_loader.get_sample_file()
            sample["time_to_failure"] = kaggle_pred / self.n_folds
            sample.to_csv("data/submission.csv")

            os.system("kaggle competitions submit -c LANL-Earthquake-Prediction -f data/submission.csv -m \"{}\""\
                .format(self.shared.selected_model + " " + datetime.now().strftime("%Y/%m/%d %H:%M:%S")))

            os.system("kaggle competitions submissions -c LANL-Earthquake-Prediction > data/kaggle_results.txt")
            
            self.shared.state_lock.acquire()
            self.shared.state.set("Submited to kaggle")
            self.shared.state_lock.release()

        # put train and test results into a dictionary
        results = dict()
        results['train_scores'] = train_scores
        results['test_scores'] = test_scores

        # put that dictionary into the queue along with the "Done" signal
        self.queue.put("Done")
        self.queue.put(results)








    
