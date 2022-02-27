#! /usr/bin/env python
import time
import pandas as pd
from pprint import pprint
from fourgp.analysis.atr_change import AtrChange
from fourgp.analysis.trend import Trend
from fourgp.database.create_tables import CreateTables
from fourgp.technicals.support_resistance import support_resistance
from fourgp.utils.config import Config
from fourgp.utils.data import Data
from fourgp.strategies.Strategy import Strategy_wrapper
from fourgp.order_management.OrderManagement import Orders
# main function to run the program collecting data and running analysis on it and using analysis to make signals.


def main(MarketPair: str):
    # whole start
    start_time0 = time.time()
    # Load configuration
    config_file = 'config.json'
    config = Config(config_file)
    config = config.config
    # create database name
    database_file_path = f'{config["database_path"]}/{config["database_name"]}'
    secondary_database_file_path = f'{config["secondary_database_path"]}/{config["secondary_database_name"]}'

    # create tables if not exist
    # TODO : use only one database connection for all the works.
    tables_create = CreateTables(
        database=database_file_path, MarketPair=MarketPair, timeframes=config['timeframe'])
    tables_create.make_tables()
    # Load exchange market data in pandas format
    data = Data(database=database_file_path, config=config, Exchange=config["Exchange"],
                MarketPair=MarketPair, timeframes=config["timeframe"], limit=config["limit"])  # FIXME: [timeframe] is not working list not single value
    # TODO : Kline naming convention is not correct and all other table names are not correct
    data.DataType = "Kline"
    Kline = data.get_data()

    # Atr(change of value per unit time) calculate and create table.
    atr=AtrChange(config)
    atr.connect()
    atr.find_atr(Database=database_file_path)
    atr.create_report()

    #  Zig zag
    zz = data.zig_zag_levels(data=Kline)
    pprint(zz["5m"])

    # Get indicators
    data.DataType = "Indicators"
    indicators = data.get_data()
    indicators = data.dict_Convert(data=indicators)
    pprint(indicators)

    # Current price of the given market pair
    current_price = data.tick_value()["close"]

    # Get support and resistance
    if config["support_resistance"]["use_from_config"] == "True":
        sr = config["support_resistance"]["sr"]
        print("Using values from configuration")
    elif config["support_resistance"]["get_from_user"] == "True":
        sr = input("Enter support and resistance values ( A list of values ): ")
        sr = config["support_resistance"]["sr"]
        print("Using values from input")
    else:
        sr = support_resistance.main_sr_dict(
            Kline, "zig_zag", config=config["support_resistance"]["create_type"])
        # print(sr)
        # clean data
        # sr = support_resistance.filter_levels(sr,size=4)
        # get nearest support and resistance levels

        sr_present = support_resistance.get_nearest_levels(support_resistance.clean_levels(
            sr)[config["primary_timeframe"]], current_price, config["support_resistance"]["size"])
        sr_info = support_resistance.get_nearest_levels(support_resistance.clean_levels(
            sr)[config["informative_timeframe"]], current_price, config["support_resistance"]["size"])
        sr_fast = support_resistance.get_nearest_levels(support_resistance.clean_levels(
            sr)[config["fast_timeframe"]], current_price, config["support_resistance"]["size"])


    print(f"Support and resistance levels: {sr_present}")
    print(f"Informative support and resistance levels: {sr_info}")
    print(f"Fast support and resistance levels: {sr_fast}")


    #  Depth of the market
    data.limit = config["depth_data_limit"]
    # data.DataType = "Depth"
    depth = data.get_market_depth()
    depth = data.make_depth(depth_data=depth)
    data.database_name = secondary_database_file_path
    data.write_file_json(depth)
    pprint(depth)
    # # asks=depth_sort.get_total_asks()
    # # print(asks)
    # # bids=depth_sort.get_total_bids()
    # # print(bids)
    # depth_sort.create_depth_chart()

    # Trend calculate
    # indicator = indicators[config["primary_timeframe"]]
    trends = Trend(Kline, indicators, sr, config)
    print(trends.trend_make())

    order = Orders(config)
    order.load()
    order.create_connection_with_exchange()
    order.get_balance()
    order.get_open_orders()
    # time end
    end_time = time.time()
    print("\n\n\n")
    # print("--- %s seconds ---" % (end_time - start_time))
    print("--- %s whole seconds ---" % (end_time - start_time0))
    print("\n\n\n")
    # strategy wrapper gets all data to make signals

    """self, config: dict, sr: dict, current_price: float, internal_sr: dict,
                 atr_informative: float, trend_value: float, depth: dict, fast_sr: dict, art_current: float"""
    Strategy = Strategy_wrapper(config,sr=sr_present,current_price=current_price,
        internal_sr=sr_info,atr_informative=0,trend_value=trend_value,depth=depth,
        fast_sr=sr_fast,art_current=0,balance=order.get_balance())
    Strategy.get_switches()
    Strategy.pre_check_values_legality()
    print(Strategy.create_sr_levels())


main("ETHUSDT")
