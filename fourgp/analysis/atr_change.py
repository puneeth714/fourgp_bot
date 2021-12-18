import ccxt
import re
import pandas_ta as ta
from tabulate import tabulate
from fourgp.utils.make_data import MakeData


class AtrChange(MakeData):
    def __init__(self, config) -> None:
        self.connection = None
        self.config = config
        self.atr_values = {}
        self.market_pair, self.timeframe, self.check_back, self.base_coin = self.get_configs()

    def get_configs(self):
        market_pair = self.config['atr_change_markets']
        timeframe = self.config['time_frame']
        check_back = self.config['atr_change_distance']
        base_coin = self.config['use_this_base_currency']
        self.connection = self.config["Exchange"]
        return market_pair, timeframe, check_back, base_coin
    def check_coin(self,pair):
        return any(re.search(base_coin+"$",pair) for base_coin in self.base_coin)
    def find_atr(self):
        if self.market_pair == "all":
            self.market_pair = self.get_coins(self.base_coin)
        atr_values = {}
        for market in self.market_pair:
            if not self.check_coin(market):
                continue
            self.data = {}
            for time in self.timeframe:
                for distance in self.check_back:
                    self.data[time+"_"+str(distance)] = self.get_values(
                        market=market, timeframe=time, distance=distance)
                    data_is = self.list_to_pandas()
                    atr_values[time+"_"+str(distance)] = self.profit_calculate(
                        self.get_present_price(data_is[time+"_"+str(distance)]), self.indicator(
                        data_is[time+"_"+str(distance)], distance))
            self.atr_values[market] = atr_values
            atr_values = {}

    def create_report(self):
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
            values=self.atr_values[market].items()
            value_list = [[value[0]]+value[1] for value in values]
            print(tabulate(value_list, headers=["Timeframe_limit","Amount", "Change",
                                                                    "Fee", "Value", "Percent Change"], tablefmt="pretty"))
            print("\n")
    def sort_values(self):
        # sort the values in the dictionary self.atr_values containing a dictionary which has values of 
        # The form [amount, change,fee_value, value_gets, percent_change]
        # sort them by percent_change in descending order
        for each_market in self.atr_values:
            for each_time in self.atr_values[each_market]:
                self.atr_values[each_market][each_time].sort(
                    key=lambda x: x[4], reverse=True)

    def get_present_price(self, data):
        return data.iloc[-1]["Close"]

    def profit_calculate(self, amount, change):
        total_fee = self.config["MakerFee"]+self.config["TakerFee"]
        fee_value = amount*total_fee
        value_gets = change-fee_value
        percent_change = value_gets*100/amount
        return [amount, round(change,2), round(fee_value,2), round(value_gets,2), round(percent_change,2)]

    def get_values(self, market: str, timeframe: str, distance: int):
        return self.connection.fetchOHLCV(market, timeframe=timeframe, limit=distance)

    def indicator(self, data: dict, distance: int):
        return float(
            ta.atr(
                data["High"], data["Low"], data["Close"], length=distance - 1
            ).to_numpy()[-1:]
        )

    def connect(self):
        if self.connection == "binance":
            self.connection = ccxt.binance()

    def get_coins(self, base_coin: list):
        vals = self.connection.fetch_tickers()
        # get all values of symbol key in vals dictionary
        if type(vals) != dict:
            print("Error Requesting Tickers")
        markets = []
        for base in base_coin:
            for key in vals:
                if "/"+base in key:
                    markets.append(key)
        return markets
