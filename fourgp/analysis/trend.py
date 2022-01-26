import time

import pandas as pd
from fourgp.utils.update_data import present_time


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

    def __ticker_price__(self) -> float:
        return self.data[self.config["primary_timeframe"]].tail(1)["Close"].values[0]

    def __get_candles__(self, timeframe,count=-1) -> pd.DataFrame:
        """Get last "count" number of candles for each timeframe

        Args:
            count (int, optional): number of candles for each timeframe. Defaults to -1 (all candles).

        Returns:
            pd.DataFrame: candles (pd.DataFrame)
        """
        __data__ = self.data if count == -1 \
                    else self.data.tail(count)

        return __data__[timeframe]

    def get_all_indicator_names(self) -> list:
        return list(self.indicators.keys())

    def __technicals__(self, time_frame: str, count=-1) -> Dict[str, pd.DataFrame]:
        """Return a dictionary containing indicator as key (string) and its value as pandas DataFrame (using self.indicators DataFrame)

        Args:
            time_frame ([str]): time as string (e.g. "1m", "5m", "1h", "1d")
            count (int, optional): number of rows to fetch for each indicator. Defaults to -1 (return all rows)

        Returns:
            Dict[str, pd.DataFrame]: key is indicator, value as pandas DataFrame
        """
        Indicators = {}
        __indicators__ = self.indicators[time_frame] if count == -1 \
            else self.indicators[time_frame].tail(count)

        for indicator in __indicators__:
            if "_" + time_frame + "_" in indicator:
                Indicators[indicator] = __indicators__[indicator]

        return Indicators

    # 6 updated trend

    def trend_find(self):
        timeframe = self.config["primary_timeframe"]
        informative_timeframe = self.config["informative_timeframe"]
        # all parameters
        # RSI_present,RSI_informative_all,close_informative_all,ema_short_present,close_present,
        # ema_long_present,ema_short_previous,ema_long_previous,macd_hist_present,
        # aroon_up_present,aroon_down_present,support_all,resistance_all,High(all)

        candles = self.__get_candles__(timeframe,-1)
        candles_informative = self.__get_candles__(informative_timeframe,-1)
        values: dict = self.__technicals__(time_frame=timeframe)
        informatives = self.__technicals__(informative_timeframe)
        # if want latest value
        self.marketpair = self.config["market_pair"][0]
        ticker: float = self.__ticker_price__(force_now=False)
        sr = self.sr
        trends = {}
        # generic
        close_values_informatives=candles_informative["Close"].values
        close_present=candles["Close"].values[0]
        # RSI
        rsi_lenght=str(self.config["periods"]["rsi"][1])
        rsi_present=values["rsi"+"_"+timeframe+"_"+rsi_lenght][-1]
        rsi_informative_lenght=self.config["limit"]["rsi"][0]
        rsi_informative=informatives["rsi"+informative_timeframe+rsi_lenght]
        RSI=self.rsi(rsi_present=rsi_present)
        RSI_informative=self.rsi_Price_Slope(rsi_informative=rsi_informative
        ,close_informative=close_values_informatives)
        # EMA
        ema_lenght=str(self.config["periods"]["ema"][1])
        ema_short_present=values["ema"+"_"+timeframe+"_"+ema_lenght][-1]
        ema_long_present=values["ema"+"_"+informative_timeframe+"_"+ema_lenght][-1]
        ema_short_previous=values["ema"+"_"+timeframe+"_"+ema_lenght][-2]
        ema_long_previous=values["ema"+"_"+informative_timeframe+"_"+ema_lenght][-2]
        EMA_short=self.ema_Short(ema_short_present,close_present)
        EMA_long=self.ema_Long(ema_long_present,close_present)
        EMA_Short_Previous=self.ema_Short_Previous(ema_short_previous,ema_short_present)
        EMA_Long_Previous=self.ema_Long_Previous(ema_long_previous,ema_long_present)
        # MACD
        Macd_lenght=str(self.config["periods"]["macd"][0])
        Macd_presnt_histogram=values["macd"+"_"+timeframe+"_"+Macd_lenght][-1][2]
        MACD=self.macd(Macd_presnt_histogram,close_present)
        # Aroon up
        aroon_up_lenght=str(self.config["periods"]["aroon"][0])
        arron_up_present=values["aroon"+"_"+timeframe+"_"+aroon_up_lenght][-1]
        AROON_UP=self.aroonUp(arron_up_present=arron_up_present)
        # Aroon down
        aroon_down_lenght=str(self.config["periods"]["aroon"][0])
        arron_down_present=values["aroon"+"_"+timeframe+"_"+aroon_down_lenght][-1]
        AROON_DOWN=self.aroonDown(aroon_down_present=aroon_down_lenght)
        # Support and Resistance
        SUPPORT_RESISTANCE=self.support_resistance(sr=sr,candles_all=candles,present_value=ticker)

        # Trend
        # for calculation of trend the upper bound and lower bound of multiplication of all parameters are used
        # Based on the upper bound value and lower bound value trend value is calculated which is in between 0 and 1(with 4 decimal places)
        # i.e theorotically if take upper bound as 1 and lower bound as 0 then trend value will be between 0 and 1

        # weight distribution of each parameter is given i note.
        TREND_MAX=None
        TREND_MIN=None
        TREND=RSI*EMA_short*EMA_long*EMA_Long_Previous*EMA_Short_Previous*MACD*AROON_UP*AROON_DOWN*SUPPORT_RESISTANCE
        return TREND
    def rsi(self,rsi_present):
        # check if rsi value is in between 30 and 70
        if rsi_present<30 or rsi_present>70:
            return rsi_present
    def rsi_Price_Slope(self,rsi_informative,close_informative):
        # Implement the slope of the price and slope of rsi vals for 
        # the last n candles
        pass
