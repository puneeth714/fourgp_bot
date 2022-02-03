import os
import sqlite3
from datetime import datetime
from time import time

import pandas as pd
from fourgp.utils.make_data import MakeData
from fourgp.utils.exchange_market_data import exchange_data
# This module is used to update the data in the dict data_pandas with the
# new data from the exchange append to the end of the data.
# The dict data_pandas is a dict of pandas dataframes with the key being
# the timeframe each timeframe is given to the run_updater function.
# The run_updater function gets present time and the latest time of the
# pandas data and then it gets the new data from the exchange and then
# it appends the new data to the end of the pandas data. after droping the
#  last row of the pandas data as it is the latest data.
# which is fetched from the exchange.


def present_time() -> int:
    """return the present time in unix format

    Returns:
        int: present time in unix format
    """
    # get current time in unix timestamp format
    now = datetime.now()
    return now.timestamp()


def time_diff_from_data(data_time: int, present_time: int, each_division: int) -> float:
    """Get the time difference from the data time and present time and divide it by the number of seconds.

    Args:
        data_time (int): The lastest time in data
        present_time (int): Present time in unix format.
        each_division (int): The number of seconds to divide into.

    Returns:
        float: The number of candles passed from the data time to the present time.
    """
    # get the time difference from the data time and present time and divide it by the number of seconds
    return (present_time - data_time)/each_division


def get_latest_time_of_pandas_data(latest_time_in_data, timeframe: str, data_pandas: pd.DataFrame = None) -> float:
    """To get the latest time of the pandas data.

    Args:
        data_pandas (pd.DataFrame): pandas dataframe of a timeframe
        timeframe (str): The timeframe of the pandas dataframe

    Returns:
        float: Returns the numbers of seconds in the timeframe.
    """
    # # get the latest time of the pandas data
    # latest_time_in_data = int(
    #     data_pandas.tail(1)["Time"])
    present_time_in_unix = present_time()
    timeframe = number_of_seconds_in_timeframe(timeframe)
    return time_diff_from_data(
        latest_time_in_data, present_time_in_unix, timeframe
    )


def number_of_seconds_in_timeframe(timeframe: str) -> int:
    # check number of seconds in the timeframe
    if timeframe == "1m":
        timeframe = 60
    elif timeframe == "3m":
        timeframe = 180
    elif timeframe == "5m":
        timeframe = 300
    elif timeframe == "15m":
        timeframe = 900
    elif timeframe == "30m":
        timeframe = 1800
    elif timeframe == "1h":
        timeframe = 3600
    elif timeframe == "4h":
        timeframe = 14400
    elif timeframe == "1d":
        timeframe = 86400
    elif timeframe == "2d":
        timeframe = 172800
    elif timeframe == "1w":
        timeframe = 604800
    elif timeframe == "1M":
        timeframe = 2592000
    elif timeframe == "1y":
        timeframe = 31536000
    return timeframe


def get_new_data(exchange: str, coin: str, timeframe: str, limit: int) -> list:
    """Get the new data from the exchange and by calling the exchange_data function in fourgp.utils.exchange_market_data.py

    Args:
        exchange (str): Name of exchange for fetching data
        coin (str): market_pair for fetching data the specified crypto exchange
        timeframe (str): timeframe for fetching data
        limit (int): How many candles to get from the exchange

    Returns:
        list: A list consists of the new data from the exchange.
    """
    # get the new data from the exchange by calling the exchange_data function.
    # exchange_data_object = exchange_data(
    #     Exchange=exchange, limit=limit+1, MarketPair=coin, timeframes=timeframe)
    pass


def insert_new_data(data_pandas: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
    """insert the new data to the end of the pandas data

    Args:
        data_pandas (pd.DataFrame): The previous pandas data
        new_data (pd.DataFrame): The new data to be appended to the end of the pandas data

    Returns:
        pd.DataFrame: The new pandas data with the new data appended to the end of the pandas data
    """
    # append data_pandas with new_data to the end in pandas format
    data_pandas = delete_old_latest_record(data_pandas)
    data_pandas = data_pandas.append(new_data, ignore_index=True)
    return data_pandas


def delete_old_latest_record(data_pandas: pd.DataFrame) -> pd.DataFrame:
    """Delete the latest record of the pandas data to insert the updated part of the data at that index
    as the close and volume of the latest record will differ if the candle is fetched before it is really fetched
    from the exchange.(even low and high might have changed)

    Args:
        data_pandas (pd.DataFrame): Dataframe from which the latest record will be deleted

    Returns:
        pd.DataFrame: The dataframe with the latest record deleted
    """
    # delete the latest record in the data
    # drop_pandas.tail(1).index will get the last row of the data
    data_pandas = data_pandas.drop(data_pandas.tail(1).index)
    return data_pandas


def run_updater(data_pandas: pd.DataFrame, timeframe: str, exchange: str, coin: str) -> list:
    """The main function to update the data in the pandas dataframe with the new data from the exchange.
    This can be called by dict_data_updater function if the pandas dataframes of different timeframes are to be updated
    all at once.

    Args:
        data_pandas (pd.DataFrame): The pandas dataframe of the timeframe to be updated
        timeframe (str): The timeframe of the pandas dataframe
        exchange (str): The exchange to get the new data from and append to the end of the pandas dataframe
        coin (str): The market pair to get the new data from and append to the end of the pandas dataframe
        (both the coin data the data to be updated should be of same market pair)

    Returns:
        list: THE new data from the exchange
    """
    # get the latest time of the pandas data
    limit = get_latest_time_of_pandas_data(data_pandas, timeframe=timeframe)
    # append the new data to the end of the pandas data
    # data_pandas = insert_new_data(data_pandas, new_data)
    return get_new_data(exchange, coin, timeframe, limit)


def dict_update_data(data_pandas: dict, exchange: str, coin: str) -> pd.DataFrame:
    """This can be the superset of the run_updater function.As the data_pandas is a dictionary of pandas dataframes
    and the run_updater function is called for each of the dataframes in the dictionary ,through number of iterations

    Args:
        data_pandas (dict): The pandas dataframes of the different timeframes to be updated
        exchange (str): The exchange to get the new data from and append to the end of the pandas dataframe
        coin (str): The market pair to get the new data from and append to the end of the pandas dataframe

    Returns:
        pd.DataFrame: The updated pandas dataframe
    """
    # send each data in dict data sent in which is a dict of pandas data
    for timeframe in data_pandas:
        list_data = run_updater(
            data_pandas[timeframe], timeframe, exchange, coin)
        data = MakeData(list_data)
        data = data.list_to_pandas()
        data_pandas[timeframe] = insert_new_data(
            data_pandas[timeframe], data)
    return data_pandas


def database_type(database):
    # check if self.database has .db or type of self.database is sqlite3.Connection
    if database.endswith(".db") or type(database) == sqlite3.Connection:
        # if yes return sqlite3
        return "sqlite3"
    elif database.endswith(".json"):
        # if yes return json
        # FIXME : not implemented yet and it should be feature format.
        return "json"
    else:
        # if no return none
        return None
