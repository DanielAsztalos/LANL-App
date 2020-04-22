# function that returns the corresponding ml model based on a name string
def get_model(name):
    if name == "RandomForestRegressor":
        from sklearn.ensemble import RandomForestRegressor
        return RandomForestRegressor()

    elif name == "SymbolicRegressor":
        from gplearn.genetic import SymbolicRegressor
        return SymbolicRegressor(500, 100, 30)

    elif name == "XGBRegressor":
        from xgboost import XGBRegressor
        return XGBRegressor()