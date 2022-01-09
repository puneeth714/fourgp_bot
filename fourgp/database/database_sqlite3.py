import sqlite3
import pandas as pd
from fourgp.utils.make_data import MakeData
from fourgp.utils.update_data import time_diff_from_data, get_new_data
# create a class to handle the sqlite3 database


class Database_sqlite3:
    def __init__(self, database: str or sqlite3.Connection, Exchange: str = None,  DataType: str = None, SymbolName: str = None, timeframe: str = None, DataLenght: int = None, data: pd.DataFrame = None):
        self.database = database
        self.exchange = Exchange
        self.DataType = DataType
        self.SymbolName = SymbolName
        self.timeframe = timeframe
        self.DataLenght = DataLenght
        self.data = data
        self.make_database()
        self.__get_table_names__()

    def make_database(self):
        # check if self.database is a string , if string use it as file path and create connection
        if isinstance(self.database, str):
            self.connection = sqlite3.connect(self.database)
        # if self.database is a sqlite3.Connection use it as connection
        elif type(self.database) == sqlite3.Connection:
            self.connection = self.database

    def __get_table_names__(self):
        # get the table names in the database
        if self.DataType == "Kline":
            table_name = "Kline_{}_{}".format(self.SymbolName, self.timeframe)
        elif self.DataType == "Indicators":
            table_name = "Indicators_{}_{}".format(
                self.SymbolName, self.timeframe)
        elif self.DataType == "Signal":
            table_name = "SignalName"
        elif self.DataType == "SignalName":
            table_name = "SignalName"
        elif self.DataType == "Depth_snapshot":
            table_name = "Depth_snapshot_{}_{}".format(
                self.SymbolName, self.timeframe)
        elif self.DataType == "Logging":
            table_name = "Logging"
        elif self.DataType == "Results":
            table_name = "Results_{}".format(self.SymbolName)
        else:
            # log table type is not found
            # rise table type error
            raise Exception("Table type is not found")
        self.table_name = table_name

    def get_data_from_database(self):
        # get the data from the database containing DataType_market_pair_timeframe (some times no timeframe and some times no market_pair is not used in name)
        # get all data from table_name
        query = "select * from {}".format(self.table_name)
        # execute query
        cursor = self.connection.cursor()
        cursor.execute(query)
        # get the data
        data = cursor.fetchall()
        # close the cursor
        cursor.close()
        tuple_pandas=MakeData(data=data)
        return tuple_pandas.tuples_to_pandas()

    def write_data_to_database(self, data_opt:pd.DataFrame=None):
        # write pandas dataframe to self.connection database
        if data_opt is None:
            self.data.to_sql(self.table_name, self.connection,
                             if_exists="append")
        else:
            data_opt.to_sql(self.table_name, self.connection,
                            if_exists="append")

    def check_database(self):
        # check if database has data for given timeframe and SymobolName and return True or False
        data = self.get_data_from_database(self)
        return len(data) > 0

    def check_updates(self):
        # check if database is up to date with data from exchange by comparing the latest timestamp in database with the present timestamp.
        # Get the last record from self.data
        last_record = self.data.iloc[-1]
        # get the timestamp from the last record
        # as the timestamp is in miliseconds
        last_timestamp = last_record["Timestamp"]/1000
        # get present time stamp
        present_timestamp = pd.Timestamp.now()
        return int(time_diff_from_data(last_timestamp, present_timestamp, int(self.timeframe)))

    def make_data_pandas(self, data):
        # convert list data to pandas dataframe using MakeData class
        data_obj = MakeData({"sqlite3": self.data})
        self.data_new = data_obj.list_to_pandas()
        return self.data_new["sqlite3"]

    def update_database(self):
        # update the database with new data from exchange
        # get the new data from exchange
        new_data = get_new_data(
            self.exchange, self.SymbolName, self.timeframe, self.check_updates())
        new_data = self.make_data_pandas()
        # if new data is not empty
        if len(new_data) > 0:
            # if the database is empty
            if not self.check_database():
                # write the new data to the database
                self.write_data_to_database(new_data)
            else:
                # delete the last record in the database
                self.delete_last_record()
                # write the new data to the database
                self.write_data_to_database(new_data)
        else:
            # if there is no new data
            pass

    def delete_last_record(self):
        # delete the last row in the database for given timeframe and market pair
        query = "delete from {} where id = (select max(id) from {})".format(
            self.table_name, self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()
