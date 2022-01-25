import sqlite3
from numpy import size

import pandas as pd
from fourgp.utils.make_data import MakeData
from fourgp.utils.update_data import get_latest_time_of_pandas_data, \
    get_new_data, time_diff_from_data, number_of_seconds_in_timeframe, present_time
import ast
# create a class to handle the sqlite3 database


class Database_sqlite3:
    def __init__(self, database: str or sqlite3.Connection, Exchange: str = None,  DataType: str = None, MarketPair: str = None, timeframe: str = None, limit: int = None, data: pd.DataFrame = None):
        self.database = database
        self.exchange = Exchange
        self.DataType = DataType
        self.MarketPair = MarketPair
        self.timeframe = timeframe
        self.limit = limit
        self.data = data
        self.make_database()

    def make_database(self):
        # check if self.database is a string , if string use it as file path and create connection
        if isinstance(self.database, str):
            self.connection = sqlite3.connect(self.database)
        # if self.database is a sqlite3.Connection use it as connection
        elif type(self.database) == sqlite3.Connection:
            self.connection = self.database

    def __get_table_name__(self):
        # get the table names in the database
        if self.DataType == "Kline":
            self.table_name = "Kline_{}_{}".format(
                self.MarketPair, self.timeframe)
        elif self.DataType == "Indicators":
            self.table_name = "Indicators_{}_{}".format(
                self.MarketPair, self.timeframe)
        elif self.DataType == "Signal":
            self.table_name = "SignalName"
        elif self.DataType == "SignalName":
            self.table_name = "SignalName"
        elif self.DataType == "Depth_snapshot":
            self.table_name = "Depth_snapshot_{}_{}".format(
                self.MarketPair, self.timeframe)
        elif self.DataType == "Logging":
            self.table_name = "Logging"
        elif self.DataType == "Results":
            self.table_name = "Results_{}".format(self.MarketPair)
        else:
            # log table type is not found
            # rise table type error
            raise Exception("Table type is not found")
            exit(1)

    def get_data_from_database(self, force_all=None):
        # get the data from the database containing DataType_market_pair_timeframe (some times no timeframe and some times no market_pair is not used in name)
        # get all data from table_name
        if force_all:
            query = "select * from {}".format(self.table_name)
        else:
            seconds = number_of_seconds_in_timeframe(
                self.timeframe)*self.limit[self.timeframe]
            timestamp_limit = (present_time()-seconds)*1000
            # select all data from table_name where timestamp is greater than equal to timestamp_limit
            query = """
            select * from  (select * from {} where Timestamp >= {} order by timestamp ASC);""".format(self.table_name, timestamp_limit)
        # # execute query
        # cursor = self.connection.cursor()
        # cursor.execute(query)
        # # get the data
        # data = cursor.fetchall()
        # # close the cursor
        # cursor.close()
        try:
            data = pd.read_sql_query(query, self.connection)
        except Exception as e:
            print(e)
            return False
        return data

    def write_data_to_database(self, data_opt: pd.DataFrame = None):
        # write pandas dataframe to self.connection database
        try:
            if data_opt is None:
                self.data.to_sql(self.table_name, self.connection,
                                 if_exists="append", index=False)
            else:
                data_opt.to_sql(self.table_name, self.connection,
                                if_exists="append", index=False)
        except Exception as e:
            # print the error formatted in red color
            print("\033[91m", e, "\033[0m")
            print(e)
            # Drop the table if it exists and write again
            self.connection.execute("drop table if exists {}".format(
                self.table_name))
            self.write_data_to_database(data_opt=data_opt)

    def check_database(self):
        # check if database has data for given timeframe and SymobolName and return True or False
        # count the number of rows in the database
        query = "select count(*) from {}".format(self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()
        # check which key in self.limit is in self.table_name and return that key
        for key in self.limit:
            if key in self.table_name:
                limit = self.limit[key]
        count = int(count[0])
        return count, limit

    def check_updates(self):
        # check if database is up to date with data from exchange by comparing the latest timestamp in database with the present timestamp.
        # Get the last record from self.data
        count, limit = self.check_database()
        if count < limit:
            return int(limit), count
        # get the last record from database by gettign the max of timestamp
        query = "select max(timestamp) from {}".format(self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        last_timestamp = int(cursor.fetchone()[0])/1000

        # last_record = self.data.iloc[-1]
        # # get the timestamp from the last record
        # # as the timestamp is in miliseconds
        # last_timestamp = last_record["Timestamp"]/1000
        # # get present time stamp
        return int(get_latest_time_of_pandas_data(latest_time_in_data=last_timestamp, timeframe=self.timeframe)), count

    def delete_last_record(self):
        # or delete coloumn in which TimeStamp is the max
        query = "delete from {} where TimeStamp = (select max(TimeStamp) from {})".format(
            self.table_name, self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def convert_From_To(self, data: pd.DataFrame, coloumn: str, typeIs: str) -> pd.DataFrame:
       # Convert the data in a coloumn of data from str to list
        if typeIs == "float":
            data = data.apply(lambda x: float(x))
        elif typeIs == "int":
            data = data.apply(lambda x: int(x))
        elif typeIs in {"list", "dict"}:
            send = data.apply(lambda x: self.string_to_list(x))
            data = send
        elif typeIs == "str":
            data = data.apply(lambda x: str(x))
        else:
            print("Type is not found")
            exit(1)
        return data

    def string_to_list(self, string: str) -> list:
        # convert string to list
        string = string.replace("[", "")
        string = string.replace("]", "")
        return string.split(",")

    def dict_Convert(self, data: pd.DataFrame) -> dict:
        for timeframe in data:
            for coloumn in data[timeframe]:
                if type(data[timeframe][coloumn][1]) == str:
                    if not self.__check_int__(data[timeframe][coloumn][1]):
                        data[timeframe][coloumn] = self.convert_From_To(
                            data[timeframe][coloumn], coloumn, "list")
                    elif self.__check_int__(data[timeframe][coloumn][1]):
                        data[timeframe][coloumn] = self.convert_From_To(
                            data[timeframe][coloumn], coloumn, "float")
                    else:
                        print("Error in converting {} to dict".format(coloumn))
                        exit(1)
        return data

    def __check_int__(self, data: str) -> bool:
        # check if data is int
        try:
            float(data)
            return True
        except ValueError:
            return False
