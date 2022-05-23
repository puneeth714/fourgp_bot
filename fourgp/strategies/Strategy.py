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
                 art_current: float, balance: dict, touched_sr: str) -> dict:
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
        self.touched_sr = touched_sr
        self.signals = {}

    def get_switches(self) -> dict:
        # returns a dict which is read from config file i.e. switches in strategy
        self.switch = self.config["strategy"]["switch"]
        return self.config["strategy"]["switch"]

    def make_orders(self):
        # call create_sr_levels, create_local_minima_maxima_levels,create_hard_real_time_levels functions and store the values in a dictionary
        # and return the dictionary
        # TODO : just make use of those functions whose weights are not zero
        self.signals["sr"] = self.create_sr_levels()
        self.signals["local_mm"] = self.create_local_minima_maxima_levels()
        self.signals["hard_rt"] = self.create_hard_real_time_levels()
        return self.signals

    def pre_check_values_legality(self):
        # check if the values are legal i.e. if the values are in the range of the market and exchange policy
        # sr should be a dictionary containing 2 keys: "support" and "resistance" and values should be a float or int and should
        # be like support should be less than resistance and present price . and resistance should be greater than current price
        if type(self.sr) == dict:
            if "support" in self.sr and "resistance" in self.sr:
                if self.sr["support"] < self.sr["resistance"] and self.current_price > self.sr["support"] and self.current_price < self.sr["resistance"]:
                    # no key value in self.balance should be less than 30 dollars.
                    # convert base to quote balance
                    least = self.__least__()
                    # self.balance["base"] = 100
                    # self.balance["quote"] = 100
                    base_to_quote_balance = self.balance["base"] * \
                        self.current_price * least
                    # TODO here only usd based quote is going to work fine -> need some enhancements to consider any coin pair.
                    if base_to_quote_balance > 10 or self.balance["quote"]*0.2 > 10:
                        if 0 <= self.trend_value <= 1:
                            return True
                        else:
                            logger.error("trend value is not in range 0-1")
                            return False
                    else:
                        logger.error("balance is less than 30 dollars")
                        return False

                else:
                    logger.error(
                        "support and resistance values are not in the right range")
                    return False
            else:
                logger.error(
                    "support and resistance values are not in the right range")
                return False
        else:
            # not a dictionary
            logger.error("sr is not a dictionary")
            return False

    def create_sr_levels(self):
        # get the upper level ie resistance and lower level ie support and get the weights of them from config i.e s_weight and r_weight
        # and multiply the weights with the balance and assign them respectively to support and resistance levels
        upper_level = self.sr["resistance"]
        lower_level = self.sr["support"]
        sr_balance_weight = self.switch["sr"]
        if sr_balance_weight == 0:
            return None
        # TODO not used s_weight and r_weight yet, they are crucial for the strategies overall performance
        s_weight = self.config["strategy"]["weight"]["s_weight"]
        r_weight = self.config["strategy"]["weight"]["r_weight"]
        # get the balance to be used for the levels
        balance_r = self.balance["base"]*sr_balance_weight
        balance_s = self.balance["quote"]*sr_balance_weight
        return {lower_level: balance_s, upper_level: balance_r}

    def create_local_minima_maxima_levels(self, force_atr=False):
        local_mm_weight = self.switch["local_mm"]
        if local_mm_weight == 0:
            return None
        if (self.internal_sr["resistance"]-self.internal_sr["support"] > self.sr["resistance"]-self.sr["support"] or force_atr):
            diff_value = self.atr_informative
            # get two values minima_signal and maxima_signal which store diff_value*self.trand_value and diff_value*(1-self.trand_value)
            minima_signal = diff_value*self.trend_value
            maxima_signal = diff_value*(1-self.trend_value)
            # use the minima_signal and maxima_signal as levels and place orders
            return {self.internal_sr["support"]: local_mm_weight*self.balance["quote"],
                    self.internal_sr["resistance"]: local_mm_weight*self.balance["base"]}
        return {self.internal_sr["support"]: local_mm_weight*self.balance["quote"],
                self.internal_sr["resistance"]: local_mm_weight*self.balance["base"]}

    def create_hard_real_time_levels(self):
        # It is mostly unpredictable , in which direction the price is going to flow.
        # The only variable that we have to predict is depth of the market.
        # call __check_depth__ method which return a dict containing side:probability
        # use the probability to decide the order type
        # value=self.__check_depth__(self.art_current)
        # and it is more predictable if the previous candle has moved drastically and we can see a little correction in it.
        # that is by checking the previous candles High-low difference and if we check it with  last five candles High-low difference
        # if it is high then we can expect the price action might see a small revesion in the next candle i.e present candle

        # but for now use just the predefined percentage and place the orders and let mover handle things
        # use self.config["strategy"]["hard_mm_distance"] dict to get the distance
        distance = self.config["strategy"]["hard_mm_distance"]
        # get the weights
        hard_mm_weight = self.switch["hard_mm"]
        if hard_mm_weight == 0:
            return None
        # make the levels
        # the upper level should be distance percent higher than the current price
        upper = self.current_price*(1+distance["upper"]/100)
        # the current price should be distance percent under the lower level
        lower = self.current_price*(1-distance["lower"]/100)
        # return the levels with values
        return {lower: hard_mm_weight*self.balance["quote"], upper: hard_mm_weight*self.balance["base"]}

    def __check_depth__(self, atr):
        # check which side of the depth is higher and return a dict containing side:probability using self.depth and self.current_price
        pass

    def post_check_values_legality(self, orders: dict):
        if type(orders) == dict:
            # the post
            #  check should check the values are legal and if not then it should return False and exeption should be raised
            # check if the values are legal i.e. if the values are in the range of the market and exchange policy
            # check the type of each key value in orders i.e sr,local_mm,hard_mm values should be of type dict
            tmp = 0
            for key, value in orders.items():
                if type(value) != dict:
                    logger.warning("value is not a dict")
                    logger.warning(
                        f"{key} is not being used for placing orders")
                    tmp += 1
                if tmp == len(orders):
                    logger.error("no order is being placed")
                    logger.warning(
                        f"{orders} is not being used for placing orders")
                    return False
                for price, amount in value.items():
                    if type(price) != float and type(price) != int:
                        logger.error("key is not a float")
                        logger.info(
                            f"{price} is not being used for placing orders")
                        return False
                    if type(amount) != float and type(amount) != int:
                        logger.error("value is not a float")
                        logger.info(
                            f"{amount} is not being used for placing orders")
                        return False
            return True
        else:
            logger.error("orders is not a dictionary")
            logger.critical(
                f"{orders} is not being used for placing orders\nExiting.....!")
            exit(1)

    def set_order_type(self):
        pass

    def __near_sr__(self):
        # check whether price is near support or resistance or in between support and resistance
        # price is near support if  price-support/resistance-support is less than 0.05
        # price is near resistance if resistance-price/resistance-support is less than 0.05
        if (self.current_price-self.sr["support"])/(self.sr["resistance"]-self.sr["support"]) < 0.05:
            return "support"
        elif (self.sr["resistance"]-self.current_price)/(self.sr["resistance"]-self.sr["support"]) < 0.05:
            return "resistance"
        else:
            return "between"

    def __atr_hl__(self):
        # check if the atr is high or low by checking the lower atr with higher atr
        # if lower_atr is less than higher_atr then it is low
        # if lower_atr is greater than higher_atr then it is high
        # THey are provided as key value pair in self.atr_informatives as low_atr and high_atr
        if self.atr_informatives["low_atr"] < self.atr_informatives["high_atr"]:
            return "low"
        elif self.atr_informatives["low_atr"] > self.atr_informatives["high_atr"]:
            return "high"
        else:
            logger.error("atr_informatives is not working as expected")
            exit(1)

    def __least__(self):
        # check which key value is least in self.config["strategy"]["switch"]
        # return the key value
        least = None
        for value in self.config["strategy"]["switch"].values():
            if least is None:
                least = value
            elif value < least:
                least = value
        if (least == 0 or least < 0):
            logger.error("value should be greater than 0")
            exit(1)
        return least
    
    def check_values(self):
        """check if the created signal are profitable if exchange fee is taken into consideration"""
        # that is read the exchange fee from the config dict with key exchange_fee and use it to calculate the profit
        # if the key is not present get the fee from the exchange and use it to calculate the profit
        fee = self.config["exchange_fee"]
        if fee is None:
            fee = self.__get_fee__()
        # check if the signal is profitable
        # if yes then return True
        # if no then return False
        
    def __get_fee__():
        # get the fee from the exchange
        pass