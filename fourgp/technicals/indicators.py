import numpy as np
import pandas_ta as ta
from fourgp.technicals.zig_zag import zig_zag_binary


class Indicators:
    def __init__(self, config, data, periods: dict = None) -> None:
        self.config = config
        self.data = data
        self.indicators = {}
        self.periods = config["periods"]

    def indicator_naming_convention(self, indicator):
        print("indicator_name"+"_"+"timeframe")
    # indicators to use ema_1m(9,50,100),ema_5m(9,50,100),ema_1h(9,50,100)
    # rsi_5m(6),rsi_1h(6),rsi_1d(6)
    # atr_5m(14),atr_1h(14),atr_1d(14)

    def make_indicator(self):
        for indicators in self.periods.keys():
            for timeframe in self.data.keys():
                for period in self.periods[indicators]:
                    if indicators == "ema":
                        self.indicators[indicators+"_"+timeframe+"_"+str(period)] = ta.ema(
                            self.data[timeframe]["Close"], length=period).to_numpy()
                    elif indicators == "rsi":
                        self.indicators[indicators+"_"+timeframe+"_"+str(period)] = ta.rsi(
                            self.data[timeframe]["Close"], length=period).to_numpy()
                    elif indicators == "atr":
                        self.indicators[indicators+"_"+timeframe+"_"+str(period)] = ta.atr(
                            self.data[timeframe]["High"], self.data[timeframe]["Low"], self.data[timeframe]["Close"], length=period).to_numpy()
                    elif indicators == "macd":
                        self.indicators[indicators+"_"+timeframe+"_"+str(period)] = ta.macd(
                            self.data[timeframe]["Close"], fastperiod=12, slowperiod=26, signalperiod=9).to_numpy()
                    elif indicators == "aroon":
                        self.indicators[indicators+"_"+timeframe+"_"+str(period)] = ta.aroon(self.data[timeframe]["High"], self.data[timeframe]["Low"]).to_numpy()
                    else:
                        print("indicator not found")
        # self.print_indicators()

    def add_indicators_to_dataframe(self):
        for indicator in self.indicators.keys():
            self.data[indicator] = self.indicators[indicator]

    def print_indicators(self):
        # print the self.indicators in formatted way
        for indicator in self.indicators.keys():
            print(indicator)
            print(self.indicators[indicator])
            print("\n")
    def zig_zag_levels(self):
        return {
            timeframe: zig_zag_binary(
                self.data[timeframe],self.config
            )
            for timeframe in self.data.keys()
        }
    def get_indicators(self):
        pass