import pandas as pd
from loguru import logger
from fourgp.order_management.OrderManagement import Orders
#  1. Support2. Resistance3.Current price4.Internal S5.Internal R6.ATR -Informative7.Trend
#  value8.depth9.Lower S10.Lower ROutput ->returns a dict containing 3 types of lists SR,local
#  min,max and real time orders pricesorder places : gets values from stategy wrapper->output ->
#  returns a dictionary containing order_type:[price_level,value,order_side,order_type,weight]


class Strategy_wrapper(Orders):
    def __init__(self, config: dict, sr: dict, current_price: float, internal_sr: dict,
                 atr_informative: float, trend_value: float, depth: dict, fast_sr: dict,
                 art_current: float, balance: dict) -> dict:
        self.config = config
        self.sr = sr
        self.current_price = current_price
        self.internal_sr = internal_sr
        self.atr_informative = atr_informative
        self.trend_value = trend_value
        self.depth = depth
        self.fast_sr = fast_sr
        self.art_current = art_current
        self.balance = balance
        self.signals = {}

    def get_switches(self) -> dict:
        # returns a dict which is read from config file i.e. switches in strategy
        self.switch=self.config["strategy"]["switches"]
        return self.config["strategy"]["switch"]

    def pre_check_values_legality(self):
        # check if the values are legal i.e. if the values are in the range of the market and exchange policy
        # sr should be a dictionary containing 2 keys: "support" and "resistance" and values should be a float or int and should
        # be like support should be less than resistance and present price . and resistance should be greater than current price
        if type(self.sr) == dict:
            if "support" in self.sr and "resistance" in self.sr:
                if self.sr["support"] < self.sr["resistance"] and self.current_price > self.sr["support"] and self.current_price < self.sr["resistance"]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def create_sr_levels(self):
        # get the upper level ie resistance and lower level ie support and get the weights of them from config i.e s_weight and r_weight
        # and multiply the weights with the balance and assign them respectively to support and resistance levels
        upper_level = self.sr["resistance"]
        lower_level = self.sr["support"]
        sr_balance_weight = self.switch["sr"]
        s_weight = self.config["strategy"]["weights"]["s_weight"]
        r_weight = self.config["strategy"]["weights"]["r_weight"]
        # get the balance to be used for the levels
        balance_r = self.balance["base"]*sr_balance_weight
        balance_s = self.balance["quote"]*sr_balance_weight
        return {lower_level: balance_s, upper_level: balance_r}

    def create_local_minima_maxima_levels(self):
        pass

    def create_hard_real_time_levels(self):
        pass

    def post_check_values_legality(self):
        pass

    def set_order_type(self):
        pass
