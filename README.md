# Fourgp Bot

A complex market making bot. Which works with both candles and ticks to create signals for cryptocurrency trading.

Api docs : [Visual api requests](http://20.204.67.186:8000/docs/) and [Api usage documentation](http://20.204.67.186:8000/redoc/)

***Please check out this link [Readme](https://github.com/puneeth714/fourgp_bot/blob/azure/README.md) for more details***
## Installation

- clone the repository [fourgp-bot](https://github.com/puneeth714/fourgp_bot.git)
- install the dependencies by running `bash install.sh`.
- **pip** install is recommended for windows users as install script is for unix or linux users.
- But there are some **_conflicts_** with pip.

## Usage

- change the configurations in `config.json` as per your requirements.
- Run the main.py file with `python3 main.py`

## Trend calculation

# Functions

- Functions :

#### RSI :

    * parameters -> self,RSI(present)
            * function -> Check if RSI is in local min or max
            * return -> RSI(present)
      # RSI_Price_Slope: More weight
            * parameters -> self,RSI(informative_all),close_prices(informative_all)
            * function ->* call get_slope(RSI)
                        * call get_slope(close_prices)
                        slope_difference = slope_RSI - slope_close_prices
                        if slope_difference is negative:
                              * return 1/slope_difference
                        elsif slope_difference is positive:
                              * return slope_difference
                        else:
                              * return 0

#### Ema_short :

    * parameters -> self,ema_short(present),value(present)
            * function->------------------------------------------Need to add functionality to check n previous values and get the average of them.(difference).
                        * difference = present value - ema_short
                        return difference

#### Ema_long :

    * parameters -> self,ema_long(present),value(present)-----last n values
            * function->------------------------------------------Need to add functionality to check n previous values and get the average of them.(difference).
                        * difference = present value - ema_long
                        return difference

#### EMA_short_Previous :

    * parameters -> self,ema_short_Previous(present),ema_short_current(present)---last n values
            * function->------------------------------------------Need to add functionality to check n previous values and get the average of them.(difference).
                        * difference = ema_short_current - ema_short_Previous
                        return difference

#### EMA_long_Previous :

    * parameters -> self,ema_long_Previous(present),ema_long_current(present)---last n values
            * function->------------------------------------------Need to add functionality to check n previous values and get the average of them.(difference).
                        * difference = ema_long_current - ema_long_Previous
                        return difference

#### Macd :

    * parameters -> self, macd_histogram(present)
            * function ->
                        * return macd_histogram(divide it by present price in trend)

#### Aroon_up :

    * parameters -> self,aroon_up(present)
            * function ->
                        * return aroon_up

#### Aroon_down :

    * parameters -> self,aroon_down(present)
            * function ->
                        * return 1/aroon_down

#### Resistance and support :

    * parameters -> self,resistance(all),support(all),High(all),present_value(present)
            * function ->
                        * near_to_s =resistance    - present value
                        * near_to_r =1/(present value - support)
                        * touched_r = touch(resistance,price(all),up)
                        * touched_s = touch(support,price(all),down)
                        * difference = near_to_s - near_to_r
                        if difference is negative:
                              * difference= 1/(present_time-touched_r time)
                        elif difference is positive:
                              * difference= present_time-touched_s time
                        else:
                              * difference= 1
                        return near_to_r*difference*touched_r

#### Touch :

    * parameters -> self,touching,prices,side
            * function ->
                  if side is up:
                        * for each_price in prices:(should iterate from present val to past)
                              if prices>touching:
                                    * return index(prices)
                        # if not touched the resistance level
                        return 1
                  elif side is down:
                        * for each_price in prices:(should iterate from present val to past)
                              if prices<touching:
                                    * return index(prices)
                        # if not touched the support level
                        return 1

#### Make_trend :

    * all parameters to make = Add up all the parameters

## Indicators Update process:

    * Get table name for that indicator
      * Check if data is present in database or not
      if true:
            * Check if data is new or not
                  * if not new
                        * Get Klines for specified timeframe and limit
                        * Calculate the indicators
                        * Write to database ---- constraint : Write to database only the new data(need a function to do so)
                  * else
                        * use that data
      else:
            * Should have klines data(as Klines is first entrance to program no problem with this test case(if klines not present))
            in database
            * Get all klines data from database/exchange
            * use it to calculate indicators
            * Write the indicators to database
            * clip the calculated data by the specified limit
      * Write to Logging table about the data collected from exchange or database.

# Version-2:

    * Get updates for limits
      * If first time or no data in database
            * Get indicators data --
                  1.Get kline data from database or already fetched data
                  2.Use the kline data and calculate the indicators.
                  3.Write the indicators to database
                  4.Clip the calculated data by the specified limit
      * else if data is present and need to update
            * Get indicators data --
                  1.Get limit data from database or already fetched data
                  2.Use the limit data and calculate the indicators.
                  3.clip the pandas data by the specified limit(Update limit)

## Atr_change Update for getting data from database: [#11](https://github.com/puneeth714/fourgp_bot/issues/11)

    * Process:
      * should inherit from Data class
            * Connect Exchange i.e set self.Exchange to exchange and call__connect_exchange__() method. --  **Optional when calling outside**
            * Connect database i.e set self.database to database path and call make_database() method.
            * Set DataType,MarketPair,Timeframe,Limit values in the for loop.
            * call database_data function with **data=False**.
            * set self.data[time+"_"+str(distance)]=data returned.

## Atr_change Update 2 for getting data from database: [#11](https://github.com/puneeth714/fourgp_bot/issues/11)

    * Process :
      * Should have Inherited AtrChange to Data class
      * Call get_data() method
      * In data_select():
            1.call find_atr()

## License

**GNU General Public License version 3**
