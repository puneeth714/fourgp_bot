import pandas as pd
import sqlite3
from fourgp.utils.__market_depth__ import DepthData
# MakeData is a class that contains methods to create dataframes from the data provided by
# the exchange (i.e data from the exchage_market_data file)


class MakeData:
    def __init__(self, data, conifg=None) -> None:
        """constructor for MakeData class that takes in a dictionary of data and a config file 
        and creates a dataframe for each of the data in the dictionary and stores it in a dictionary
        of dataframes

        Args:
            data (dict): [data from exchange i.e data from exchange_market_data]] 
            conifg ([dict]): [config parameters as a dictionary]
        """
        self.data = data
        self.config = conifg

    def list_to_pandas(self, data=None) -> dict:
        """list_to_pandas method takes in a dictionary of data and creates a dataframe for each of the data in the dictionary

        Returns:
            dict: dictionary of dataframes for furthur processing in analysis and signal processing
        """
        if data is not None:
            self.data = data
        pandas_data = {}
        for each_data in self.data.keys():
            # Dataframe contains the columns names as Time,Open,High,Low,Close,Volume.
            df = pd.DataFrame(self.data[each_data], columns=[
                              'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            # Add the dataframe to the dictionary of pandas_data
            pandas_data[each_data] = df
        self.data = pandas_data
        return pandas_data

    def time_convert(self):
        # convert unix time to datetime format in pandas dataframe "Time" column
        for each_data in self.data:
            self.data[each_data]['Time'] = pd.to_datetime(
                self.data[each_data]['Time'], unit='ms')
        return self.data

    def tuples_to_pandas(self, data=None) -> pd.DataFrame:
        # convert tuple of values Timestamp , Open , High , Low , Close , Volume into pandas dataframe
        if data is None:
            return pd.DataFrame(self.data, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
        else:
            return pd.DataFrame(data, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
