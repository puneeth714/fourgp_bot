from time import time
import pandas as pd
import numpy as np


def dict_pandas(data_dictionary, column_data):
    data = {}
    for timeframe in column_data:
        for name in data_dictionary:
            if timeframe in name:
                if timeframe not in data:
                    data[timeframe] = {"Timestamp": list(
                        column_data[timeframe]), name: convert_to_string(data_dictionary[name])}
                else:
                    data[timeframe].update(
                        {name: convert_to_string(data_dictionary[name])})
        data[timeframe] = pd.DataFrame(data[timeframe])
    return data


def convert_to_string(data):
    if type(data) != list and type(data) != np.ndarray and not type(data):
        return data
    if type(data[0]) == np.ndarray:
        return list(map(lambda x: str(list(x)), data))
    else:
        return list(map(str, data))


def get_specific_column(data: dict, column_name: str):
    for timeframe in data:
        data[timeframe] = data[timeframe][column_name].to_numpy()
    return data
