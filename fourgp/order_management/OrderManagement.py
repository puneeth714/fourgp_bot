import ccxt
import dotenv
import logging
import os
import pandas as pd
import time
from pprint import pprint


class Orders:
    def __init__(self, config) -> None:
        self.config = config

    def load(self):
        # read the .env file and load the variables
        if dotenv.load_dotenv(".env"):
            # create a dictionary of the variables
            self.__variables__ = {
                "apiKey": os.getenv("apiKey"),
                "apiSecret": os.getenv("apiSecret"),
            }
        else:
            print("Please create a .env file")
            exit(1)

    def create_connection_with_exchange(self):
        self.exchange = ccxt.binance()
        self.exchange.apiKey = self.__variables__["apiKey"]
        self.exchange.secret = self.__variables__["apiSecret"]
        # load the markets from the exchange
        self.markets = self.exchange.load_markets()

    def get_balance(self):
        # get all balance from the exchange
        try:
            self.balance = self.exchange.fetch_balance()
        except:
            print(
                "might be a problem with the exchange or the apiKey and apiSecret or not connected to internet")
            exit(1)
        self.__read_quote_base__()
        self.quote_balance = self.balance[self.quote]["free"]
        self.base_balance = self.balance[self.base]["free"]
        # print(f"Quote value is = {self.quote_balance}\nBase value is  = {self.base_balance}\n")
        return {"base": self.base_balance, "quote": self.quote_balance}

    def __read_quote_base__(self):
        # read the quote and base from the config file
        # FIXME : This is not the best way to do this. Works with only first one pair.
        try:
            self.base = self.config["market_pair"][0][:3]
            self.quote = self.config["market_pair"][0][3:]
            # print(self.quote,self.base)
        except Exception as e:
            print(e)
            print("Please enter the quote and base in the config file")
            print("Please check OrderManagement.py file for more details")
            exit(1)
        
    def get_open_orders(self):
        # get open orders from the exchange of the market pair
        # print(self.open_orders)
        return self.exchange.fetch_open_orders(self.config["market_pair"][0])
    
    def send_orders(self):
        pass
    
    
