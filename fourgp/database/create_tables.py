# check if the tables(Kline,Indicators,Signals,Depth_snapshot,Logging,Results) exits in the database data and create them if not
# check if Kline table exists in the database and create it if not with columns Timestamp , Open , High , Low , Close , Volume
import sqlite3
from loguru import logger

class CreateTables:
    def __init__(self, database, MarketPair: list, timeframes: list, drop: bool = None):
        self.database = database
        self.MarketPair = MarketPair
        self.timeframes = timeframes
        self.drop = drop
        self.connection = self.make_database()

    def make_database(self):
        if type(self.database) == sqlite3.Connection:
            logger.debug("Database already exists and is connected")
            return self.database
        elif type(self.database) == str:
            logger.debug("Database is a string")
            logger.debug("Connecting to database")
            connection = sqlite3.Connection(self.database)
            logger.debug("Database connected")
            return connection
        elif self.database is None:
            # use data/data.db file for database
            logger.debug("Database is None and will be created at default location")
            connection = sqlite3.Connection("data/data.db")
            return connection

    def make_tables(self):
        for market_pair in [self.MarketPair]:
            for timeframe in self.timeframes:
                logger.debug("Creating table for {} {}".format(market_pair, timeframe))
                self.create_table(market_pair, timeframe)

    def create_table(self, SymbolName, timeframe, connection: sqlite3.Connection = None):
        if connection is None:
            connection = self.connection
        # create table in connection database with convention Kline_SymbolName_timeframe with columns Timestamp , Open , High , Low , Close , Volume
        try:
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
            logger.debug("Table Kline_{}_{} created".format(SymbolName, timeframe))
        except Exception as e:
            logger.error("Error creating table Kline_{}_{}".format(SymbolName, timeframe))
            logger.error(e)
        try:
            # create table in connection database with convention Indicators_SymbolName_timeframe with columns Timestamp , CreationTime , IndicatorsName , values
            query = """
            create table if not exists Indicators_{}_{}(
                Timestamp text NOT NULL PRIMARY KEY,
                IndicatorsName text,
                Vals text
                )""".format(SymbolName, timeframe)
            connection.execute(query)
            connection.commit()
            logger.debug("Table Indicators_{}_{} created".format(SymbolName, timeframe))
        except Exception as e:
            logger.error("Error creating table Indicators_{}_{}".format(SymbolName, timeframe))
            logger.error(e)
        try:
            # create table in connection database with convention Tick_SymbolName with columns Timestamp , values
            query = """
            create table if not exists Tick_{}(
                Timestamp text NOT NULL PRIMARY KEY,
                Vals text
                )""".format(SymbolName)
            connection.execute(query)
            connection.commit()
            logger.debug("Table Tick_{} created".format(SymbolName))
        except Exception as e:
            logger.error("Error creating table Tick_{}".format(SymbolName))
            logger.error(e)
        try:
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
            logger.debug("Table SignalName created")
        except Exception as e:
            logger.error("Error creating table SignalName")
            logger.error(e)
        try:
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
            logger.debug("Table Depth_snapshot created")
        except Exception as e:
            logger.error("Error creating table Depth_snapshot")
            logger.error(e)
        try:
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
            logger.debug("Table Logging created")
        except Exception as e:
            logger.error("Error creating table Logging")
            logger.error(e)
        try:
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
            logger.debug("Table Results_{} created".format(SymbolName))
        except Exception as e:
            logger.error("Error creating table Results_{}".format(SymbolName))
            logger.error(e)

    def drop_tables(self):
        for market_pair in self.MarketPair:
            for timeframe in self.timeframe:
                logger.debug("Dropping table for {} {}".format(market_pair, timeframe))
                try:
                    self.drop_table(market_pair, timeframe)
                except Exception as e:
                    logger.error(e)

    def drop_table(self, SymbolName, timeframe):
        try:
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
        except Exception as e:
            logger.error("Error dropping table for {} {}".format(SymbolName, timeframe))
            logger.error(e)