# create an application of fast api
import json
import fastapi
from main import *
# Get the coin name and timeframe
app = fastapi.FastAPI()


@app.get("/")
def root():
    return {"message": "I can provide trend analysis for any coin and timeframe"}
# ping ok


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/coins/{coin}")
def get_coin_timeframe(coin: str):
    # Get the data from the API
    data = main(MarketPair=coin)
    # Return the data
    return data
# Get indicator values


@app.get("/coins/{coin}/timeframe/{timeframe}/indicators/{indicator}")
def get_indicators(indicator: str, coin: str, timeframe: str):
    # Get the data from the API
    data = main(MarketPair=coin, indicator=indicator, time_frame=timeframe)
    # Return the data
    return data


# get all the timeframe and indicators available
# read the config.json file
with open("config.json") as json_file:
    config = json.load(json_file)


@app.get("/indicators/")
def get_indicators():
    return config["periods"]


@app.get("/timeframe/")
def get_timeframe():
    return config["time_frame"]

# get current value of the coin


@app.get("/coins/{coin}/current_value")
def get_current_value(coin: str):
    data = main(MarketPair=coin, value_only=True)
    return {coin: data}

# get last n klines


@app.get("/coins/{coin}/timeframe/{timeframe}/klines/{n}")
def get_klines(coin: str, timeframe: str, n: int):
    data = main(MarketPair=coin, time_frame=timeframe, klines=int(n))
    return data
