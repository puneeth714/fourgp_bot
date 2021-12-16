import time
from fourgp.technicals.indicators import Indicators
from fourgp.utils.config import Config
from fourgp.utils.exchange_market_data import exchange_data
from fourgp.utils.make_data import MakeData, DepthData
from fourgp.utils.update_data import dict_update_data, run_updater, insert_new_data
from fourgp.technicals.support_resistance import support_resistance
from fourgp.technicals.candlesticks.candle_patterns import CandlePatterns
from fourgp.technicals.market_data import marketTrades
from fourgp.analysis.trend import Trend
# main function to run the program collecting data and running analysis on it and using analysis to make signals.


def main(market_pair: str):
    # whole start
    start_time0 = time.time()
    # Load configuration
    config_file = 'config.json'
    config = Config(config_file)
    config = config.config

    # Load exchange market data in pandas format
    data = exchange_data(config=config, coin=market_pair, depth=5000)
    depth = data.get_market_depth()
    ccxt_object = data.exchange
    data = data.data

    # time start
    start_time = time.time()
    # Make data
    make_data = MakeData(data, config)
    # print(make_data.list_to_pandas()["1m"].tail(10))

    # # update data if needed and rewrite existing data
    # time.sleep(60)
    # new_data = run_updater(
    #     make_data.list_to_pandas()["1m"], "1m", config["Exchange"], "ETHUSDT")
    # make_data1 = MakeData(new_data, config)
    # data = insert_new_data(
    #     make_data.list_to_pandas()["1m"], make_data1.list_to_pandas()["1m"])
    # print(data.tail(10))

    # # or make iterative data
    # data2 = dict_update_data(
    #     make_data.list_to_pandas(), config["Exchange"], "ETHUSDT")
    # print(data2)

    # Make indicators
    indicators = Indicators(config, make_data.list_to_pandas())
    indicators.make_indicator()
    # indicators.add_indicators_to_dataframe()
    #  Make support and resistance
    # convert unix time to datetime
    df = make_data.data
    print(df["5m"].tail(10))
    # print(df["1m"].head(200))
    df = make_data.time_convert()
    print(df["5m"].tail(10))

    #     #write dataframe to csv samples.txt
    # df["1m"].to_csv("samples.txt")

    # Get support and resistance
    sr = support_resistance.main_sr_dict(
        df, "zig_zag", config=config["support_resistance"]["create_type"])
    # print(sr)

    # clean data
    sr = support_resistance.clean_levels(sr)
    print("\n\n\n")
    print(sr)

    # # candlestick pattern
    # candle = CandlePatterns(make_data.list_to_pandas(), ["all",
    #                         "CDL3LINESTRIKE", "CDLENGULFING", "CDLHAMMER", "CDLINVERTEDHAMMER"],trucate=5)
    # candle.__filter_data_latest__()
    # print(candle.get_pattern_names())

    # #trades of the market
    # market= marketTrades(market_pair,ccxt_object,config["market_data_limit"])
    # print(market.get_trades())

    # #  Depth of the market
    # depth_sort=DepthData(depth)
    # a=depth_sort.get_depth_prices()
    # print(a)
    # b=depth_sort.get_total_asks()
    # print(b)
    # c=depth_sort.get_total_bids()
    # print(c)
    # depth_sort.create_depth_chart()

    # #  Zig zag
    # zz=indicators.zig_zag_levels()
    # print(zz["5m"])

    # Trend calculate
    indicator = indicators.indicators
    trends = Trend(df, indicator, sr, config)
    print(trends.trend_make())
    # time end
    end_time = time.time()
    print("\n\n\n")
    print("--- %s seconds ---" % (end_time - start_time))
    print("--- %s whole seconds ---" % (end_time - start_time0))


main("ETHUSDT")
