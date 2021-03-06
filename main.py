#! /usr/bin/env python
import time

import pandas as pd
from loguru import logger
import sys
from fourgp.analysis.atr_change import AtrChange
from fourgp.analysis.trend import Trend
from fourgp.database.create_tables import CreateTables
from fourgp.order_management.OrderManagement import Orders
from fourgp.strategies.Strategy import Strategy_wrapper
from fourgp.technicals.support_resistance import support_resistance
from fourgp.utils.config import Config
from fourgp.utils.data import Data

# main function to run the program collecting data and running analysis on it and using analysis to make signals.


@logger.catch
def main(MarketPair: str):
    # whole start
    logger.remove()
    logger.add(level="INFO", sink=sys.stdout)
    start_time0 = time.time()
    # Load configuration
    config_file = 'config.json'
    config = Config(config_file)
    config = config.config
    # create database name
    database_file_path = f'{config["database_path"]}/{config["database_name"]}'
    logger.debug(f'Database file path is set to : {database_file_path}')
    secondary_database_file_path = f'{config["secondary_database_path"]}/{config["secondary_database_name"]}'
    logger.debug(
        f'Secondary Database file path is set to : {secondary_database_file_path}')
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

    # # Atr(change of value per unit time) calculate and create table.
    # atr = AtrChange(config)
    # atr.connect()
    # atr.find_atr(Database=database_file_path)
    # atr.create_report()

    #  Zig zag
    zz = data.zig_zag_levels(data=Kline)
    logger.info(f"Zig zag levels for {MarketPair} are caculated")

    # Get indicators
    data.DataType = "Indicators"
    indicators = data.get_data()
    indicators = data.dict_Convert(data=indicators)
    # pprint(indicators)

    # Current price of the given market pair
    current_price = data.tick_value()["close"]

    # Get support and resistance
    if config["support_resistance"]["use_from_config"] == "True":
        sr = config["support_resistance"]["sr"]
        logger.info("Using values from configuration")
    elif config["support_resistance"]["get_from_user"] == "True":
        sr = input("Enter support and resistance values ( A list of values ): ")
        sr = config["support_resistance"]["sr"]
        logger.info("Using values from input")
    else:
        sr = support_resistance.main_sr_dict(
            Kline, "zig_zag", config=config["support_resistance"]["create_type"])
        # print(sr)
        # clean data
        # sr = support_resistance.filter_levels(sr,size=4)
        # get nearest support and resistance levels

    # Trend

    sr_present = support_resistance.get_nearest_levels(support_resistance.clean_levels(
        sr)[config["primary_timeframe"]], current_price, config["support_resistance"]["size"])
    sr_info = support_resistance.get_nearest_levels(support_resistance.clean_levels(
        sr)[config["informative_timeframe"]], current_price, config["support_resistance"]["size"])
    sr_fast = support_resistance.get_nearest_levels(support_resistance.clean_levels(
        sr)[config["fast_timeframe"]], current_price, config["support_resistance"]["size"])
    # FIXME the resistance levels should not be None for the strategy to work properly
    # need to fix the support and resistance levels finding logic
    if sr_present is None:
        sr_present = sr_info
    if sr_fast is None:
        if sr_present is None:
            sr_fast = sr_info
        sr_fast = sr_present

    logger.info(f"Support and resistance levels: {sr_present}")
    logger.info(f"Informative support and resistance levels: {sr_info}")
    logger.info(f"Fast support and resistance levels: {sr_fast}")

    #  Depth of the market
    data.limit = config["depth_data_limit"]
    # data.DataType = "Depth"
    depth = data.get_market_depth()
    data.bids = depth["bids"]
    data.asks = depth["asks"]

    # depth = data.make_depth(depth_data=depth)
    # data.database_name = secondary_database_file_path
    # data.write_file_json(depth)
    # pprint(depth)

    # # asks=depth_sort.get_total_asks()
    # # print(asks)
    # # bids=depth_sort.get_total_bids()
    # # print(bids)
    # depth_sort.create_depth_chart()

    # Trend calculate
    # indicator = indicators[config["primary_timeframe"]]
    trends = Trend(Kline, indicators, sr_present, config)
    trend_value = trends.trend_make()
    logger.info(f"Trend value: {trend_value}")
    # get touched_sr returns s or r , stores in touched_sr
    trends.touch(touching=sr_info, prices=Kline[config["primary_timeframe"]])

    order = Orders(config)
    order.load()
    order.create_connection_with_exchange()
    logger.debug(f"balance is {order.get_balance()}")
    logger.debug(f"open orders are {order.get_open_orders()}")
    if (order.get_open_orders() != []):
        logger.warning("There are open orders in the exchange!!!")
    # tmp
    sr_present = support_resistance.tmp_make(sr_present)
    sr_info = support_resistance.tmp_make(sr_info)
    sr_fast = support_resistance.tmp_make(sr_fast)
    Strategy = Strategy_wrapper(config, sr=sr_present, current_price=current_price, internal_sr=sr_info,
                                atr_informative=float(indicators[config["primary_timeframe"]]["atr_{}_14".format(
                                    config["primary_timeframe"])][-1:]),
                                trend_value=trend_value, depth=depth, fast_sr=sr_fast,
                                art_current=float(indicators[config["informative_timeframe"]]["atr_{}_{}".format(
                                    config["informative_timeframe"], 14)][-1:]),
                                balance=order.get_balance(), touched_sr=trends.touched_sr)

    Strategy.get_switches()
    if not Strategy.pre_check_values_legality():
        logger.critical("Values are not legal")
        logger.info("Exiting")
        exit(1)
    orders = Strategy.make_orders()
    logger.debug(orders)
    # do post checks of the order
    if not Strategy.post_check_values_legality(orders):
        logger.critical("Order values are not legal")
        exit(1)

    # time end
    end_time = time.time()
    print("\n\n\n")
    # print("--- %s seconds ---" % (end_time - start_time))
    logger.info("--- %s whole seconds ---" % (end_time - start_time0))
    print("\n\n\n")
    # strategy wrapper gets all data to make signals


main("ETHUSDT")
