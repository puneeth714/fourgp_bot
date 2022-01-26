import time
import pandas as pd
from pprint import pprint
from fourgp.analysis.atr_change import AtrChange
from fourgp.analysis.trend import Trend
from fourgp.database.create_tables import CreateTables
from fourgp.technicals.candlesticks.candle_patterns import CandlePatterns
from fourgp.technicals.indicators import Indicators
from fourgp.technicals.market_data import marketTrades
from fourgp.technicals.support_resistance import support_resistance
from fourgp.utils.config import Config
from fourgp.utils.data import Data
from fourgp.utils.exchange_market_data import exchange_data
from fourgp.utils.make_data import DepthData, MakeData
from fourgp.utils.update_data import (dict_update_data, insert_new_data,
                                      run_updater)
from fourgp.utils.utilities import dict_pandas, get_specific_coloumn
# main function to run the program collecting data and running analysis on it and using analysis to make signals.

def main(MarketPair: str):
    # whole start
    start_time0 = time.time()
    # Load configuration
    config_file = 'config.json'
    config = Config(config_file)
    config = config.config
    # create database name
    database_file_path = config['database_path']+"/"+config['database_name']
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
    make_data = data.get_data()

    # atr=AtrChange(config)
    # atr.connect()
    # atr.find_atr(Database=database_file_path)
    # atr.create_report()

    # # update data if needed and rewrite existing data
    # sleep for 60 seconds
    # time.sleep(60)
    # fetch the data again (auto updation is done)
    # make_data = data.get_data()

    # # Make indicators
    # indicators = Indicators(config, make_data)
    # indicators.make_indicator()
    # # add timestamp of make_data to indicators
    # # get the timestamp from make_data and return it
    # coloumn_name = "Timestamp"
    # coloumn_data = get_specific_coloumn(
    #     data=make_data, coloumn_name=coloumn_name)
    # indicator_data = dict_pandas(
    #     data_dictionary=indicators.indicators, coloumn_data=coloumn_data)
    # data.data = indicator_data
    # # write the data to the database
    # data.DataType = "Indicators"
    # data.put_data()
    # Get indicators
    data.DataType = "Indicators"
    indicators = data.get_data()
    indicators = data.dict_Convert(data=indicators)
    pprint(indicators)
    #  Make support and resistance
    # convert unix time to datetime
    # df = make_data
    # df = make_data.time_convert()
    # print(df["5m"].tail(10))

    #     #write dataframe to csv samples.txt
    # df["1m"].to_csv("samples.txt")

    # Get support and resistance
    sr = support_resistance.main_sr_dict(
        make_data, "zig_zag", config=config["support_resistance"]["create_type"])
    # print(sr)
    # clean data
    sr = support_resistance.clean_levels(sr)
    sr = support_resistance.get_support_resistance(sr_each=sr)
    # convert sr dictionary to dataframe
    # sr = pd.DataFrame(sr)



    # # candlestick pattern
    # candle = CandlePatterns(make_data.list_to_pandas(), ["all",
    #                         "CDL3LINESTRIKE", "CDLENGULFING", "CDLHAMMER", "CDLINVERTEDHAMMER"],trucate=5)
    # candle.__filter_data_latest__()
    # print(candle.get_pattern_names())

    # #trades of the market
    # market= marketTrades(market_pair,ccxt_object,config["market_data_limit"])
    # print(market.get_trades())

    #  Depth of the market
    data.limit = config["depth_data_limit"]
    depth=data.get_market_depth()
    depth_sort=DepthData(depth)

    # asks=depth_sort.get_total_asks()
    # print(asks)
    # bids=depth_sort.get_total_bids()
    # print(bids)
    depth_sort.create_depth_chart()

    # #  Zig zag
    # zz=indicators.zig_zag_levels()
    # print(zz["5m"])


    #Trend calculate
    # indicator = indicators[config["primary_timeframe"]]
    trends = Trend(make_data, indicators, sr, config)
    print(trends.trend_find())
    # time end
    end_time = time.time()
    print("\n\n\n")
    # print("--- %s seconds ---" % (end_time - start_time))
    print("--- %s whole seconds ---" % (end_time - start_time0))
    # files=AtrChange(config)
    # files.connect()
    # files.find_atr()
    # # files.sort_values()
    # files.create_report()
main("ETHUSDT")
