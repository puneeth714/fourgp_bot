import re
import ccxt
import pandas_ta as ta
from fourgp.utils.make_data import MakeData
from fourgp.utils.data import Data
from tabulate import tabulate


class AtrChange(Data):
    def __init__(self, config) -> None:
        self.connection_exchange = None
        self.config = config
        self.atr_values = {}
        tmp = self.get_configs()
        self.market_pair, self.timeframe_atr, self.check_back, self.base_coin = tmp[
            0], tmp[1], tmp[2], tmp[3]
        del tmp

    def get_configs(self) -> list:
        market_pair = self.config['atr_change_markets']
        timeframe = self.config['time_frame']
        check_back = self.config['atr_change_distance']
        base_coin = self.config['use_this_base_currency']
        self.connection_exchange = self.config["Exchange"]
        return [market_pair, timeframe, check_back, base_coin]

    def check_coin(self, pair) -> str:
        return any(re.search(base_coin+"$", pair) for base_coin in self.base_coin)

    def find_atr(self, Database=True) -> None:
        if self.market_pair == "all":
            self.market_pair = self.get_coins(self.base_coin)
        if Database != None:
            self.database = Database
            self.make_database()
        atr_values = {}
        for market in self.market_pair:
            if not self.check_coin(market):
                continue
            data_is = {}
            for time in self.timeframe_atr:
                for distance in self.check_back:
                    if Database != None:
                        self.DataType = "Kline"
                        self.MarketPair = market
                        self.timeframes = [time]
                        self.limit = {time: distance}
                        data = self.database_data()
                        if self.__check_status__(data=data):
                            data_is[time+"_"+str(distance)
                                    ] = data[list(data.keys())[0]]
                        else:
                            data_is = self.__no_database__(
                                time=time, distance=distance, market=market)
                    else:
                        data_is = self.__no_database__(
                            time=time, distance=distance, market=market)
                    atr_values[time+"_"+str(distance)] = self.profit_calculate(
                        self.get_present_price(data_is[time+"_"+str(distance)]), self.indicator(
                            data_is[time+"_"+str(distance)], distance))
            self.atr_values[market] = atr_values
            atr_values = {}

    def __check_status__(self, data):
        try:
            if data[list(data.keys())[0]].empty == False:
                return True
        except:
            if data[list(data.keys())[0]] != False:
                return False

    def __no_database__(self, time, distance, market):
        self.data = {}
        self.data[time+"_"+str(distance)] = self.get_values(
            market=market, timeframe=time, distance=distance)
        return self.list_to_pandas()

    def create_report(self) -> None:
        # # create a pretty format terminal output for the dictionary self.atr_values containing a
        # #  dictionary which has values of the form [amount, change,fee_value, value_gets, percent_change]
        # # using rich module
        # for market in self.atr_values:
        #     for time in self.atr_values[market]:
        #             pretty.pprint(market)
        #             pretty.pprint(time)
        #             pretty.pprint(self.atr_values[market][time])
        #             print("\n")
        # tabulate the values in the dictionary self.atr_values containing a dictionary which has values of
        # The form [amount, change,fee_value, value_gets, percent_change]
        # using tabulate module with table format as pretty and html
        for market in self.atr_values:
            print(market)
            print("\n")
            values = self.atr_values[market].items()
            value_list = [[value[0]]+value[1] for value in values]
            print(tabulate(value_list, headers=["Timeframe_limit", "Amount", "Change",
                                                "Fee", "Value", "Percent Change"], tablefmt="pretty"))
            print("\n")

    def sort_values(self) -> None:
        # sort the values in the dictionary self.atr_values containing a dictionary which has values of
        # The form [amount, change,fee_value, value_gets, percent_change]
        # sort them by percent_change in descending order
        for each_market in self.atr_values:
            for each_time in self.atr_values[each_market]:
                self.atr_values[each_market][each_time].sort(
                    key=lambda x: x[4], reverse=True)

    def get_present_price(self, data) -> float:
        return data.iloc[-1]["Close"]

    def profit_calculate(self, amount, change) -> list:
        total_fee = self.config["MakerFee"]+self.config["TakerFee"]
        fee_value = amount*total_fee
        value_gets = change-fee_value
        percent_change = value_gets*100/amount

        # (Values with 2 decimal places are not accurate and some are showing 0.00)
        return [amount, f"{change:.12f}".rstrip("0"), f"{fee_value:.6f}".rstrip("0"),
                        f"{value_gets:.12f}".rstrip("0"), f"{percent_change:.12f}".rstrip("0")]

    def get_values(self, market: str, timeframe: str, distance: int) -> list:
        return self.connection_exchange.fetchOHLCV(market, timeframe=timeframe, limit=distance)

    def indicator(self, data: dict, distance: int) -> float:
        return float(
            ta.atr(
                data["High"], data["Low"], data["Close"], length=distance - 1
            ).to_numpy()[-1:]
        )

    def connect(self) -> None:
        if self.connection_exchange == "binance":
            self.connection_exchange = ccxt.binance()

    def get_coins(self, base_coin: list) -> list:
        vals = self.connection_exchange.fetch_tickers()
        # get all values of symbol key in vals dictionary
        if type(vals) != dict:
            print("Error Requesting Tickers")
        markets = []
        for base in base_coin:
            for key in vals:
                if "/"+base in key:
                    markets.append(key)
        return markets
