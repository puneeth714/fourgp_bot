import sqlite3

from fourgp.database.database_generic import Database_generic
from fourgp.database.database_sqlite3 import Database_sqlite3
# TODO : added need updates in doc string indicators
from fourgp.technicals.indicators import Indicators
from fourgp.utils.exchange_market_data import exchange_data
from fourgp.utils.make_data import MakeData
from fourgp.utils.update_data import (database_type, dict_update_data,
                                      insert_new_data, run_updater)
from fourgp.utils.utilities import dict_pandas, get_specific_column
from fourgp.utils.market_depth import DepthData

# from main import database_file_path


class Data(exchange_data, MakeData, Database_sqlite3, Database_generic, Indicators, DepthData):
    def __init__(self, database: str  = None, config=None, Exchange: str = None,
                 MarketPair: str = None, timeframes: list = None, limit: list = None, data=None, DataType: str = None, ForceGet: bool = False) -> None:
        """The Data class is used to get data from the exchange and to make data for analysis and also to store 
        data in a database. By default the data is stored in a sqlite3 database.
        But if data is not stored in a database, it can be fetched from the exchange and stored in a database.
        Data class inherits from exchange_data for getting data from the exchange and MakeData for making data 
        for analysis , and Database_sqlite3 for storing data in a database or fetching data from a database.

        Args:
            database (str_or_sqlite3.Connection, optional): The path to database file or connection object. Defaults to None.
            config (dict, optional): Dictionary values of configurations. Defaults to None.
            Exchange (str, optional): Name of the exchange. Defaults to None.
            MarketPair (str, optional): Market pair used for getting or analysis of data. Defaults to None.
            timeframes (list, optional): The timeframe for which the data to be fetched. Defaults to None.
            limit (list, optional): The limit for how much data to be fetched. Defaults to None.
            data ([type], optional): Optional parameter for convertion of list data to pandas. Defaults to None.
            DataType (str, optional): Which type of data to be fetched (Kline , indicators , ticks , depth_snapshot , logging , results(any).). Defaults to None.
            ForceGet (bool, optional): Force the process of fetching the specified data from exchange rather from database. Defaults to False.
        """
        self.database = database
        self.config = config
        self.Exchange = Exchange
        self.MarketPair = MarketPair
        self.timeframes = timeframes
        self.limit = limit
        self.data = data
        self.DataType = DataType
        self.config_to_variables()
        self.__connect_exchange__()
        self.make_database()

    def get_data(self):
        # get the data from the database containing DataType_market_pair_timeframe (some times no timeframe and some times no market_pair is not used in name)
        # get all data from table_name
        count = {}
        limit = self.limit.copy()
        # Fixed-FIXME : Count is not correct shouldn't be size of table but size of data needed.
        for self.timeframe in self.timeframes:
            self.__get_table_name__()
            self.limit[self.timeframe], count[self.timeframe] = self.check_updates()
        self.data = self.data_select(limit=limit)
        # write the data dict of pandas to a database
        self.put_data(self.data)
        self.limit = limit
        del limit
        # If count is less than the limit, then fetch the data  again from the database
        return self.database_data()

    def database_data(self, force=None) -> dict:
        data = {}
        for self.timeframe in self.timeframes:
            self.__get_table_name__()
            data[self.timeframe] = self.get_data_from_database(force_all=force)
        return data

    def put_data(self, data):
        # write data to database from the dictionary of pandas data
        self.data = data.copy()
        # 8 THe tables created when self.DataType is Indicators are not desirable.
        for self.timeframe in data.keys():
            self.__get_table_name__()
            self.data = data[self.timeframe]
            self.write_data_to_database()

    def data_select(self, limit=None):
        if self.DataType == 'Kline':
            self.data = self.get_data_klines()
            return self.list_to_pandas()
        elif self.DataType == 'Indicators':
            self.DataType = "Kline"
            limit_copy = self.limit.copy()
            self.limit = limit
            self.data = self.database_data()
            self.limit = limit_copy
            self.DataType = "Indicators"
            self.periods = self.config["periods"]
            # create indicators dictionary
            self.indicators = {}
            self.make_indicator()
            # add timestamp of make_data to indicators
            # get the timestamp from make_data and return it
            column_name = "Timestamp"
            column_data = get_specific_coloumn(
                data=self.data, column_name=coloumn_name)
            indicator_data = dict_pandas(
                data_dictionary=self.indicators, column_data=coloumn_data)
            return self.clip_data(indicator_data, limit_copy)

    def clip_data(self, data, limit) -> dict:
        # clip the data from the database
        # just get last limit number of data from the pandas data
        for each in data.keys():
            for timeframe in limit.keys():
                if timeframe in each:
                    data[each] = data[each].tail(limit[timeframe])
                    continue
        return data
