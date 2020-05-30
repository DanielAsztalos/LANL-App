import json
import os
from errors import FileNotFoundError

# a class that loads the parameter grids and default parameters of the
# ml models
class ParamLoader:
    def __init__(self):
        if not os.path.exists("data/config.json"):
            raise FileNotFoundError


        # load json file that contains the param grids
        with  open("data/config.json", "r") as inf:
            data = json.load(inf)

        # parse loaded data
        for model in data:
            for param in model["params"]:
                if param["type"] == 1 or param["type"] == 2:
                    vals = param["vals"]
                    if type(vals[2]) == int:
                        param["vals"] = list(range(vals[0], vals[1] + 1, vals[2]))
                    else:
                        param["vals"] = []
                        x = vals[0]
                        while x <= vals[1]:
                            param["vals"].append(round(x, 3))
                            x += vals[2]
        
        self.data = data

    def get_model_names(self):
        return [x["model_type"] for x in self.data]

    def get_param_grid(self, model):
        grid = dict()
        types = []
        for model_ in self.data:
            if model_["model_type"] == model:
                for param in model_["params"]:
                    grid[param["name"]] = param["vals"]
                    types.append(param["type"])
        return grid, types

    def get_hints_of_model(self, model_name):
        hints = []
        for model_ in self.data:
            if model_["model_type"] == model_name:
                for param in model_["params"]:
                    hints.append(param["hint"])
                break
        return hints

    # modify default parameter values for a given model
    def modify_defaults(self, defaults):
        with open("data/defaults.json", "r") as inf:
            data = json.load(inf)

        model = list(defaults.keys())[0]
        data[model] = defaults[model]

        with open("data/defaults.json", "w") as outf:
            json.dump(data, outf)

    # load default parameters
    def load_defaults(self):
        with open("data/defaults.json", "r") as inf:
            data = json.load(inf)

        return data
    