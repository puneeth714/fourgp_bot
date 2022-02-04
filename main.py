import time
import pandas as pd
from pprint import pprint
from fourgp.analysis.atr_change import AtrChange
from fourgp.analysis.trend import Trend
from fourgp.database.create_tables import CreateTables
from fourgp.technicals.support_resistance import support_resistance
from fourgp.utils.config import Config
from fourgp.utils.data import Data
# main function to run the program collecting data and running analysis on it and using analysis to make signals.


def main(MarketPair: str,time_frame:str=None,indicator=None,value_only=None,klines:int=None):
    # whole start
    start_time0 = time.time()
    # Load configuration
    config_file = 'config.json'
    config = Config(config_file)
    config = config.config
    # create database name
    database_file_path = config['database_path']+"/"+config['database_name']
    secondary_database_file_path = config['secondary_database_path']+"/"+config['secondary_database_name']
    # create tables if not exist
    # TODO : use only one database connection for all the works.
    tables_create = CreateTables(
        database=database_file_path, MarketPair=MarketPair, timeframes=config['time_frame'])
    tables_create.make_tables()
    # Load exchange market data in pandas format
    data = Data(database=database_file_path, config=config, Exchange=config["Exchange"],
                MarketPair=MarketPair, timeframes=config["time_frame"], limit=config["limit"])  # FIXME: [timeframes] is not working list not single value
    # TODO : Kline naming convention is not correct and all other table names are not correct
    data.DataType = "Kline"
    Klines = data.get_data()
    if klines is not None:
        Klines = dict(Klines[time_frame][-klines:])
        return Klines
    if value_only is not None:
        return float(Klines["1m"].tail(1)["Close"])
    

    # # Atr(change of value per unit time) calculate and create table.
    # atr=AtrChange(config)
    # atr.connect()
    # atr.find_atr(Database=database_file_path)
    # atr.create_report()

    #  Zig zag
    zz=data.zig_zag_levels(data=Klines)
    pprint(zz)
    
    # Get indicators
    data.DataType = "Indicators"
    indicators = data.get_data()
    indicators = data.dict_Convert(data=indicators)
    pprint(indicators)
    if indicator is not None:
        send={}
        for indicator_name in indicators[time_frame]:
            if indicator in indicator_name:
                send[indicator_name]=list(indicators[time_frame][indicator_name].tail(1).values)
        return send


    # Get support and resistance
    if  config["support_resistance"]["use_from_config"] == "True":
        sr = config["support_resistance"]["sr"]
        print("Using values from configuration")
    elif input("Do you want to use values in configuration :\nTrue/False :") == "True":
        sr = config["support_resistance"]["sr"]
        print("Using values from input")
    else:
        sr = support_resistance.main_sr_dict(
            Klines, "zig_zag", config=config["support_resistance"]["create_type"])
        # print(sr)
        # clean data
        sr = support_resistance.filter_levels(sr)
        sr = support_resistance.clean_levels(sr)
        sr = support_resistance.get_support_resistance(sr_each=sr)
    print(sr)

    #  Depth of the market
    data.limit = config["depth_data_limit"]
    # data.DataType = "Depth"
    depth=data.get_market_depth()
    depth=data.make_depth(depth_data=depth)
    data.database_name=secondary_database_file_path
    data.write_file_json(depth)
    pprint(depth)
    # # asks=depth_sort.get_total_asks()
    # # print(asks)
    # # bids=depth_sort.get_total_bids()
    # # print(bids)
    # depth_sort.create_depth_chart()


    # Trend calculate
    # indicator = indicators[config["primary_timeframe"]]
    trends = Trend(Klines, indicators, sr, config)
    trend=trends.trend_find()

    # time end
    end_time = time.time()
    print("\n\n\n")
    # print("--- %s seconds ---" % (end_time - start_time))
    print("--- %s whole seconds ---" % (end_time - start_time0))
    print("\n\n\n")
    return trend
# print(main("ETHUSDT"))
