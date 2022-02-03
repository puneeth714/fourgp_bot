# check if the tables(Kline,Indicators,Signals,Depth_snapshot,Logging,Results) exits in the database data and create them if not
# check if Kline table exists in the database and create it if not with columns Timestamp , Open , High , Low , Close , Volume
import sqlite3


class CreateTables:
    def __init__(self, database, MarketPair: list, timeframes: list, drop: bool = None):
        self.database = database
        self.MarketPair = MarketPair
        self.timeframes = timeframes
        self.drop = drop
        self.connection = self.make_database()

    def make_database(self):
        if type(self.database) == sqlite3.Connection:
            return self.database
        elif type(self.database) == str:
            connection = sqlite3.Connection(self.database)
            return connection
        elif self.database is None:
            # use data/data.db file for database
            connection = sqlite3.Connection("data/data.db")
            return connection

    def make_tables(self):
        for market_pair in [self.MarketPair]:
            for timeframe in self.timeframes:
                self.create_table(market_pair, timeframe)

    def create_table(self, SymbolName, timeframe, connection: sqlite3.Connection = None):
        if connection is None:
            connection = self.connection
        # create table in connection database with convention Kline_SymbolName_timeframe with columns Timestamp , Open , High , Low , Close , Volume
        query = """
        create table if not exists Kline_{}_{}(
            Timestamp text NOT NULL PRIMARY KEY,
            Open real,
            High real,
            Low real,
            Close real,
            Volume real
            )""".format(SymbolName, timeframe)
        connection.execute(query)
        connection.commit()
        # create table in connection database with convention Indicators_SymbolName_timeframe with columns Timestamp , CreationTime , IndicatorsName , values
        query = """
        create table if not exists Indicators_{}_{}(
            Timestamp text NOT NULL PRIMARY KEY,
            IndicatorsName text,
            Vals text
            )""".format(SymbolName, timeframe)
        connection.execute(query)
        connection.commit()
        # create table in connection database with convention Tick_SymbolName with columns Timestamp , values
        query = """
        create table if not exists Tick_{}(
            Timestamp text NOT NULL PRIMARY KEY,
            Vals text
            )""".format(SymbolName)
        connection.execute(query)
        connection.commit()
        # create table in connection database with convention SignalName with columns CreationTime , Buy[ A list of prices for which the signal is buy] , Sell[ A list of prices for which the signal is sell],
        # StopLoss[ A list of prices for which the signal is StopLoss] , TakeProfit[ A list of prices for which the signal is takeprofit]
        query = """
        create table if not exists SignalName(
            CreationTime text NOT NULL PRIMARY KEY,
            Buy text,
            Sell text,
            StopLoss text,
            TakeProfit text
            )"""
        connection.execute(query)
        connection.commit()
        # create table in connection database with convention Depth_snapshot_SymbolName_timeframe with columns CreationTime , Price , Quantity , Total_Quantity , Total_Value , Total_Base_Quantity , Total_Base_Value , Total_Quote_Quantity , Total_Quote_Value , Is_Buy_Order , Is_Best_Price_Match , Time_Stamp
        query = """
        create table if not exists Depth_snapshot(
            CreationTime text NOT NULL PRIMARY KEY,
            Price real,
            Bids real,
            Asks real
            )"""
        connection.execute(query)
        connection.commit()
        # create table in connection database with convention Logging with columns TimeStamp,CreationTime , Log_Type , Log_Message
        query = """
        create table if not exists Logging(
            TimeStamp text NOT NULL PRIMARY KEY,
            CreationTime text,
            Log_Type text,
            Log_Message text
            )"""
        connection.execute(query)
        connection.commit()
        # create table in connection database with convention Results_SymbolName with columns CreationTime , pnlOverall , Status , Time_Stamp
        query = """
        create table if not exists Results_{}(
            CreationTime text NOT NULL PRIMARY KEY,
            pnlOverall real,
            Status text,
            TimeStamp text
            )""".format(SymbolName)
        connection.execute(query)
        connection.commit()

    def drop_tables(self):
        for market_pair in self.MarketPair:
            for timeframe in self.timeframe:
                self.drop_table(market_pair, timeframe)

    def drop_table(self, SymbolName, timeframe):

        connection = self.connection
        # drop table in connection database with convention Kline_SymbolName_timeframe
        query = """
        drop table if exists Kline_{}_{}""".format(SymbolName, timeframe)
        connection.execute(query)
        connection.commit()
        # drop table in connection database with convention Indicators_SymbolName_timeframe
        query = """
        drop table if exists Indicators_{}_{}""".format(SymbolName, timeframe)
        connection.execute(query)
        connection.commit()
        # drop table in connection database with convention Tick_SymbolName
        query = """
        drop table if exists Tick_{}""".format(SymbolName)
        connection.execute(query)
        connection.commit()
        # drop table in connection database with convention SignalName
        query = """
        drop table if exists SignalName"""
        connection.execute(query)
        connection.commit()
        # drop table in connection database with convention Depth_snapshot_SymbolName_timeframe
        query = """
        drop table if exists Depth_snapshot_{}_{}""".format(SymbolName, timeframe)
        connection.execute(query)
        connection.commit()
        # drop table in connection database with convention Logging
        query = """
        drop table if exists Logging"""
        connection.execute(query)
        connection.commit()
        # drop table in connection database with convention Results_SymbolName
        query = """
        drop table if exists Results_{}""".format(SymbolName, timeframe)
        connection.execute(query)
        connection.commit()
