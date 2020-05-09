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

    elif name == "CatBoost":
        from catboost import CatBoostRegressor
        return CatBoostRegressor()
    
    elif name == "LGBM":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(metric="mae", early_stopping_round=2000)