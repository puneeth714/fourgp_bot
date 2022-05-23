import os
from distutils.command.config import config

import ccxt
from dotenv import load_dotenv


# exchange_data class is used to get data from exchange after
# connecting to a specific exchange given the exchange name from config file config.json
class exchange_data:
    def __init__(self, config=None, Exchange: str = None, MarketPair: str = None, timeframes: list = None, limit: list = None) -> None:
        """exchage_data class constructor

        Args:
            config ([dictionary]): pre defined values read from config.json
            coin ([str]): market pair to fetch data from exchange for analysis
        """
        self.config = config
        self.Exchange = Exchange
        self.MarketPair = MarketPair
        self.timeframes = timeframes
        self.limit = limit
        self.config_to_variables()
        self.__connect_exchange__()
        # self.taker=self.__get_fee__('taker')
        # self.maker=self.__get_fee__('maker')

    def config_to_variables(self) -> None:
        """config_to_variables method reads the config file config.json and sets the values to the class variables
        """
        if self.config != None:
            self.load_from_config()
        elif (
            self.Exchange is None
            and self.MarketPair is None
            and self.timeframes is None
            and self.limit is None
        ):
            self.get_from_user()
        else:
            print("May have unhandled exception or error or total perfect")
            print(f"Check this vars: exchange = {self.Exchange}, coin = {self.MarketPair}, timeframes = {self.timeframes}, limit = {self.limit}")

    def get_from_user(self):
        print('No config file found')
        self.Exchange = input('Enter exchange: ')
        self.coin = input('Enter market pair: ')
        self.timeframes = input('Enter time frames: ')
        self.limit = input('Enter limit: ')

    def load_from_config(self):
        self.Exchange = self.config['Exchange']
        self.timeframes = self.config['timeframe']
        self.limit = self.config['limit']

    def __connect_exchange__(self) -> None:
        """__connect_exchange__ method connects to exchange given exchange name from config file config.json 
        and sets the exchange object of ccxt library to self.exchange
        """
        # load .env file
        load_dotenv()
        if "binance" in self.Exchange:
            self.Exchange = ccxt.binance()
        elif "bitfinex" in self.Exchange:
            self.Exchange = ccxt.bitfinex()
        elif "bitmex" in self.Exchange:
            self.Exchange = ccxt.bitmex()
        elif "bittrex" in self.Exchange:
            self.Exchange = ccxt.bittrex()
        elif "coinbase" in self.Exchange:
            self.Exchange = ccxt.coinbasepro()
        elif "kraken" in self.Exchange:
            self.Exchange = ccxt.kraken()
        elif "poloniex" in self.Exchange:
            self.Exchange = ccxt.poloniex()
        else:
            print('No exchange found')
            self.Exchange = input('Enter exchange: ')
            if self.Exchange == 'binance':
                self.Exchange = ccxt.binance()

    def get_data_klines(self) -> dict:
        """get_data method returns the data from exchange after 
        connecting to exchange and fetching the specified market pair data

        Returns:
            dict: [Kline data from exchange for a given market pair ,specified timeframe ,specified range]
        """
        # load the marketa
        # self.exchange.load_markets()
        if self.Exchange.has['fetchOHLCV']:
            # fetch the data using the fetchOHLCV method
            # If the limit =0 then the fetch should be skipped
            
            data = {
                timeframe: self.Exchange.fetch_ohlcv(
                    self.MarketPair, timeframe, limit=int(self.limit[timeframe])
                )
                for timeframe in self.timeframes
                if self.limit[timeframe] != 0
            }

        else:
            # exit if the exchange does not support fetching OHLCV
            print('Exchange does not support fetching OHLCV')
            exit(1)
        return data

    def get_market_depth(self)->dict:
        if self.Exchange.has['fetchOrderBook']:
            data_market_depth = self.Exchange.fetchOrderBook(
                self.MarketPair, limit=int(self.limit))
        else:
            print('Exchange does not support fetching order book')
            exit(1)
        return data_market_depth

    def tick_value(self):
        return self.Exchange.fetch_ticker(self.MarketPair)

    def __get_fee__(self, side: str):
        return self.Exchange.load_markets()[self.MarketPair][side]

