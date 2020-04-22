from threading import Lock

# a shared object that contains data that is shared between different
# components of the application
class SharedObject:
    def __init__(self, state, root, selected_model=None, param_grid=None, cv=None,\
                train_X = None, train_y = None, test_X = None, test_y = None, queue=None):

        self.state_lock = Lock()
        self.state = state
        self.root = root
        self.selected_model_lock = Lock()
        self.selected_model = selected_model
        self.param_grid_lock = Lock()
        self.param_grid = param_grid

        self.data_lock = Lock()
        self.train_X, self.train_y, self.test_X, self.test_y = (train_X, train_y, test_X, test_y)
