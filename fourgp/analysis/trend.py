import time

import pandas as pd
from fourgp.utils.update_data import present_time
from main import marketpair


class Trend:
    def __init__(self, data: dict, indicators: dict, sr: dict, config: dict) -> None:
        """Trend class constructor method.

        Args:
            data (dict): data is a dictionary of pandas dataframes.
            indicators (dict): indicators is a dictionary of pandas dataframes containing required indicators.
            sr (dict): support and resistance levels
            config (dict): config is a dictionary of configuration parameters.
        """
        self.data = data
        self.config = config
        self.indicators = indicators
        self.sr = sr
        self.trend = {}

    def trends_calc(self) -> None:
        time_frame = self.config["primary_timeframe"]
        values: dict = self.__technicals__(time_frame)
        informatives = self.__technicals__(
            self.config["informative_timeframe"])
        ticker: float = self.__ticker_price__()
        trends = {}
        if values["rsi_{}_6".format(time_frame)][0] < 30 and values[
                "ema_{}_9".format(time_frame)][0] > values["ema_{}_9".format(time_frame)][1] and values["macd_{}_1".format(time_frame)][0][2] > values["macd_{}_1".format(time_frame)][1][2] or (values["macd_{}_1".format(time_frame)][0][2] > 0 and values["macd_{}_1".format(time_frame)][1][2] < 0):
            print("Trend is changing from down to up")
        elif values["rsi_{}_6".format(time_frame)][1] < values["rsi_{}_6".format(time_frame)][0] and values["ema_{}_9".format(time_frame)][0] < values["ema_{}_9".format(time_frame)][1] and values["ema_{}_50".format(time_frame)][0] < values["ema_{}_9".format(time_frame)][0] and values["macd_{}_1".format(time_frame)][0][2] > values["macd_{}_1".format(time_frame)][1][2] and values["macd_{}_1".format(time_frame)][0][2] > 0:
            print("Trend is Uptrend")
        elif values["rsi_{}_6".format(time_frame)][0] > 70 and values["ema_{}_9".format(time_frame)][0] < values["ema_{}_9".format(time_frame)][1] and values["macd_{}_1".format(time_frame)][0][2] < values["macd_{}_1".format(time_frame)][1][2] or (values["macd_{}_1".format(time_frame)][0][2] < 0 and values["macd_{}_1".format(time_frame)][1][2] > 0):
            print("Trend is changing from up to down")
        elif values["rsi_{}_6".format(time_frame)][1] > values["rsi_{}_6".format(time_frame)][0] and values["ema_{}_9".format(time_frame)][0] < values["ema_{}_9".format(time_frame)][1] and values["ema_{}_50".format(time_frame)][0] > values["ema_{}_9".format(time_frame)][0] and values["macd_{}_1".format(time_frame)][0][2] < values["macd_{}_1".format(time_frame)][1][2] and values["macd_{}_1".format(time_frame)][0][2] < 0:
            print("Trend is Downtrend")
        else:
            print("Trend is stable")
            for keys in values:
                print(keys + "  : " +
                      str(values[keys][1])+" -> "+str(values[keys][0]))

    def trend_make(self) -> float:
        time_frame = self.config["primary_timeframe"]
        candles = self.__get_candles__(2)
        values: dict = self.__technicals__(time_frame)
        informatives = self.__technicals__(
            self.config["informative_timeframe"])
        ticker: float = self.__ticker_price__()
        sr = self.sr
        trends = {}
        previous_candle = [candles["Open"].values[0],
                           candles["Close"].values[0]]
        present_candle = [candles["Open"].values[1],
                          candles["Close"].values[1]]
        candle = self.candle_check(previous_candle, present_candle)
        rsi_val = [values["rsi_{}_6".format(
            time_frame)][0], values["rsi_{}_6".format(time_frame)][1]]
        RSI = self.RSI_check(rsi_val)
        macd_val = [values["macd_{}_1".format(
            time_frame)][0][2], values["macd_{}_1".format(time_frame)][1][2]]
        MACD = self.Macd_check(macd_val)
        aroon_val = [values["aroon_{}_1".format(
            time_frame)][0], values["aroon_{}_1".format(time_frame)][1]]
        Aroon = self.Aroon_check(aroon_val)
        ema_val = [[values["ema_{}_9".format(time_frame)][0], values["ema_{}_9".format(time_frame)][1]], [
            values["ema_{}_50".format(time_frame)][0], values["ema_{}_50".format(time_frame)][1]]]
        Ema = self.Ema_check(ema_val=ema_val)
        support_resistance_val = self.sr
        candles_check = self.__get_candles__(5)
        present_val = ticker
        SR = self.SR_check(support_resistance_val,
                           candles_check, present_val=present_val)
        return candle+RSI+MACD+Aroon+Ema+SR

    def SR_check(self, support_resistance_val, candles_check: pd.DataFrame, present_val)->float:
        positives = {}
        negatives = {}
        for sr in support_resistance_val:
            change = present_val-sr
            if change > 0:
                positives[sr] = change
            else:
                negatives[sr] = change
        # find the smallest positive value in positives dictionary and the largest  value in negatives dictionary
        if positives:
            smallest_positive_value_change = min(positives, key=positives.get)
            smallest_positive_value = positives[smallest_positive_value_change]
        else:
            smallest_positive_value = 0
        if negatives:
            largest_negative_value_change = max(negatives, key=negatives.get)
            largest_negative_value = negatives[largest_negative_value_change]
        else:
            largest_negative_value = 0
        # Check if the candle crossed the support and resistance lines
        i = 5
        for low in candles_check["Low"].values:
            i -= 1
            if low < largest_negative_value:
                return 0.0
        for high in candles_check["High"].values:
            i -= 1
            if high > smallest_positive_value:
                return 0.2

    def get_support_resistance(self) -> float:
        sr = []
        for i in self.sr:
            sr += self.sr[i]
        return sr

    def Ema_check(self, ema_val) -> float:
        if ema_val[0][0] > ema_val[0][1]:
            if ema_val[1][0] > ema_val[1][1]:
                return 0.2*(ema_val[0][0]-ema_val[0][1])*100/ema_val[0][0]
            return 0.1*(ema_val[0][0]-ema_val[0][1])*100/ema_val[0][0]
        elif ema_val[0][0] < ema_val[0][1]:
            if ema_val[1][0] < ema_val[1][1]:
                return 0.01*(ema_val[0][1]-ema_val[0][0])*100/ema_val[0][0]
            return -0.05*(ema_val[0][0]-ema_val[0][1])*100/ema_val[0][0]

    def Aroon_check(self, aroon_val) -> float:
        if aroon_val[0][1] > aroon_val[0][0]:
            if aroon_val[0][1] > 90 or aroon_val[0][0] < 20:
                return 0.05
            return 0.1
        elif aroon_val[0][0] > aroon_val[1][0]:
            return 0.0
        elif aroon_val[0][1] < 20 or aroon_val[0][0] > 90:
            return 0.05

    def Macd_check(self, macd_val) -> float:  # sourcery skip: remove-redundant-if
        if macd_val[1] < macd_val[0]:
            if macd_val[1] < 0:
                return 0.2
            return 0.1
        elif macd_val[1] < macd_val[0]:
            if macd_val[1] > 0:
                return 0.1
            return 0.05
        elif macd_val[1] > macd_val[0]:
            if macd_val[1] > 0:
                return 0.00
            return 0.03
        elif macd_val[1] == macd_val[0]:
            if macd_val[1] < 0:
                return 0.05
            return 0.1

    def RSI_check(self, rsi_val) -> float:
        if rsi_val[0] < 30 or rsi_val[1] < 38:
            weight = rsi_val[0]*100/70*0.1/100
            if rsi_val[0] > rsi_val[1]:
                return 0.2+weight
            return 0.1+weight
        elif rsi_val[0] > 70 or rsi_val[0] > 40:
            if rsi_val[0] > rsi_val[1]:
                return 0.1
            return 0.0
        elif rsi_val[0] > 65 and rsi_val[1] > rsi_val[0]:
            weight = 70-rsi_val[0]*100/70*0.1/100
            return 0.0
        elif rsi_val[1] > 40:
            return 0.05

    def candle_check(self, previous_candle, present_candle) -> float:
        if previous_candle[0] > previous_candle[1] and present_candle[0] < present_candle[1]:
            return 0.2
        elif previous_candle[0] < previous_candle[1] and present_candle[0] < present_candle[1]:
            return 0.1
        elif previous_candle[0] < previous_candle[1] and present_candle[0] > present_candle[1]:
            return 0.0
        elif previous_candle[0] > previous_candle[1] and present_candle[0] > present_candle[1]:
            return 0.05
        else:
            print("Candle is Confusing ://")
            return 0.0

    def __ticker_price__(self,force_now=False) -> float:
        if force_now==True:
            import ccxt
            ccxt.binance().fetch_ticker(marketpair)["last"]
        return self.data[self.config["primary_timeframe"]].tail(1)["Close"].values[0]

    def __get_candles__(self, number_of) -> pd.DataFrame:
        return self.data[self.config["primary_timeframe"]].tail(number_of)

    def get_all_indicator_names(self) -> list:
        return list(self.indicators.keys())

    def __technicals__(self, time_frame,force_all=False) -> None:
        #TODO : combine both if statement and outer boaddy make function more scalable given a parameter count of indicators the function will return last count of indicators
        if force_all==True:
            indicators = {
                indicator: self.indicators[indicator]
                for indicator in self.indicators
                if "_" + time_frame + "_" in indicator
            }

            return  indicators
        return {
            indicator: [
                self.indicators[indicator][len(
                    self.indicators[indicator]) - 1],
                self.indicators[indicator][len(
                    self.indicators[indicator]) - 2],
            ]
            for indicator in self.indicators
            if "_"+time_frame+"_" in indicator
        }
    #6 updated trend
    def Trend(self):
        timeframe=self.config["primary_timeframe"]
        informative_timeframe=self.config["informative_timeframe"]
        # all parameters 
            # RSI_present,RSI_informative_all,close_informative_all,ema_short_present,close_present,
            # ema_long_present,ema_short_previous,ema_long_previous,macd_hist_present,
            # aroon_up_present,aroon_down_present,support_all,resistance_all,High(all)
        
        candles = self.__get_candles__(2)
        values: dict = self.__technicals__(time_frame=timeframe)
        informatives = self.__technicals__(informative_timeframe)
        # if want latest value
        self.marketpair=marketpair
        ticker: float = self.__ticker_price__(force_now=False)
        sr = self.sr
        trends = {}
        # RSI
        rsi_lenght=self.config["limit"]["rsi"][1]
        rsi_present=values["rsi"+timeframe+rsi_lenght][0]
        rsi_informative_lenght=self.config["limit"]["rsi"][0]
        rsi_informative=informatives["rsi"+informative_timeframe+rsi_lenght]
        previous_candle = [candles["Open"].values[0],
                           candles["Close"].values[0]]
        present_candle = [candles["Open"].values[1],
                          candles["Close"].values[1]]
