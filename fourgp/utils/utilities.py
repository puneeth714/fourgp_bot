from operator import le
from time import time
import pandas as pd
def __append_array_to_pandas(pandas_data:pd.DataFrame,array_name,array):
    pandas_data["zig_zag_levels"]=array
    return pandas_data
def dict_pandas(pandas_data_dictionary,array_dictionary):
    if len(pandas_data_dictionary)==len(array_dictionary):
        for timeframe in pandas_data_dictionary:
            pandas_data_dictionary[timeframe]=__append_array_to_pandas(pandas_data_dictionary[timeframe],timeframe,array_dictionary[timeframe])
    return pandas_data_dictionary