import numpy
from zigzag import *
import pandas as pd
def zig_zag_binary(data: pd.DataFrame, config: dict) -> numpy:
    # Find the zig zag binary for the data in ohcl format
    numpy_data = pandas_to_numpy(data,"Close")
    return peak_valley_pivots(numpy_data, 0.01,-0.01)
    # peak_valley_poivot()
def pandas_to_numpy(data:pd.DataFrame,part:str):
    return data[part].to_numpy()
