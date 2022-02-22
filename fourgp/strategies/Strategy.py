import pandas as pd
from loguru import logger
#  1. Support2. Resistance3.Current price4.Internal S5.Internal R6.ATR -Informative7.Trend value8.depth9.Lower S10.Lower ROutput ->returns a dict containing 3 types of lists SR,local min,max and real time orders pricesorder places : gets values from stategy wrapper->output -> returns a dictionary containing order_type:[price_level,value,order_side,order_type,weight]
class Strategy_wrapper:
    def __init__(self,config:dict,sr:dict,current_price:float,internal_sr:dict,atr_informative:float,trend_value:float,depth:dict,fast_sr:dict,art_current:float)->dict:
        self.config=config
        self.sr=sr
        self.current_price=current_price
        self.internal_sr=internal_sr
        self.atr_informative=atr_informative
        self.trend_value=trend_value
        self.depth=depth
        self.fast_sr=fast_sr
        self.art_current=art_current

    def get_switches(self)->dict:
        # returns a dict which is read from config file i.e. switches in strategy
        return self.config["switches"]
        
    def present_balance(self)->dict:
        # returns a dict containing present balance of quote and asset pairs in the given account.
        pass
    def pre_check_values_legality(self):
        pass
    def create_sr_levels(self):
        pass
    def create_local_minima_maxima_levels(self):
        pass
    def create_hard_real_time_levels(self):
        pass
    def post_check_values_legality(self):
        pass
    def set_order_type(self):
        pass