import os
from distutils.command.config import config

import ccxt
from dotenv import load_dotenv

# exchange_data class is used to get data from exchange after 
# connecting to a specific exchange given the exchange name from config file config.json 
class exchange_data:
    def __init__(self, config=None,exchange:str=None, coin:str=None,timeframes:list=None,limit:list=None,depth:int=None) -> None:
        """exchage_data class constructor

        Args:
            config ([dictionary]): pre defined values read from config.json
            coin ([str]): market pair to fetch data from exchange for analysis
        """
        self.config = config
        self.exchange = exchange
        self.market_pair = coin
        self.timeframes = [timeframes]
        self.limit = limit
        self.config_to_variables()
        self.__connect_exchange__()
        self.data
        self.config = config
        self.depth = depth
        # self.taker=self.__get_fee__('taker')
        # self.maker=self.__get_fee__('maker')
    def config_to_variables(self) -> None:
        """config_to_variables method reads the config file config.json and sets the values to the class variables
        """        
        if self.config!=None:
            self.load_from_config()
        elif (
            self.exchange is None
            and self.market_pair is None
            and self.timeframes is None
            and self.limit is None
        ):
            self.get_from_user()
        else:
            print("May have unhandled exception or error or total perfect")
            print("Check this vars: exchange = {}, coin = {}, timeframes = {}, limit = {}".format(self.exchange,self.market_pair
            ,self.timeframes,self.limit))

    def get_from_user(self):
        print('No config file found')
        self.exchange = input('Enter exchange: ')
        self.coin = input('Enter market pair: ')
        self.timeframes = input('Enter time frames: ')
        self.limit = input('Enter limit: ')

    def load_from_config(self):
        self.exchange = self.config['Exchange']
        self.timeframes = self.config['time_frame']
        self.limit = self.config['limit']


    def __connect_exchange__(self) -> None:
        """__connect_exchange__ method connects to exchange given exchange name from config file config.json 
        and sets the exchange object of ccxt library to self.exchange
        """        
        # load .env file
        load_dotenv()
        if "binance" in self.exchange:
            self.exchange = ccxt.binance()
        elif "bitfinex" in self.exchange:
            self.exchange = ccxt.bitfinex()
        elif "bitmex" in self.exchange:
            self.exchange = ccxt.bitmex()
        elif "bittrex" in self.exchange:
            self.exchange = ccxt.bittrex()
        elif "coinbase" in self.exchange:
            self.exchange = ccxt.coinbasepro()
        elif "kraken" in self.exchange:
            self.exchange = ccxt.kraken()
        elif "poloniex" in self.exchange:
            self.exchange = ccxt.poloniex()
        else:
            print('No exchange found')
            self.exchange = input('Enter exchange: ')
            if self.exchange == 'binance':
                self.exchange = ccxt.binance()

    def get_data_klines(self) -> dict:
        """get_data method returns the data from exchange after 
        connecting to exchange and fetching the specified market pair data

        Returns:
            dict: [klines data from exchange for a given market pair ,specified timeframe ,specified range]
        """        
        #load the marketa        
        # self.exchange.load_markets()
        if self.exchange.has['fetchOHLCV']:
            # fetch the data using the fetchOHLCV method
            data = {
                time_frame: self.exchange.fetch_ohlcv(
                    self.market_pair, time_frame, limit=int(self.limit[time_frame])
                )
                for time_frame in self.timeframes
            }

        else:
            # exit if the exchange does not support fetching OHLCV
            print('Exchange does not support fetching OHLCV')
            exit(1)
        return data
    def get_market_depth(self):
        if self.exchange.has['fetchOrderBook']:
            data_market_depth = self.exchange.fetchOrderBook(self.market_pair, limit=int(self.depth))
        else:
            print('Exchange does not support fetching order book')
            exit(1)
        return data_market_depth
    def tick_value(self):
        return self.exchange.fetch_ticker(self.market_pair)
        
    def __get_fee__(self,side:str):
        return self.exchange.load_markets()[self.market_pair][side]
