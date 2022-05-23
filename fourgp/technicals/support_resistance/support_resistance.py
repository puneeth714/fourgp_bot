import pandas as pd
from loguru import logger
from fourgp.technicals.support_resistance.pricelevels.cluster import ZigZagClusterLevels
from fourgp.technicals.support_resistance.pricelevels.cluster import RawPriceClusterLevels
from fourgp.technicals.support_resistance.pricelevels.scoring.touch_scorer import TouchScorer

# from fourgp.analysis.support_resistance.pricelevels.visualization.levels_with_zigzag import plot_with_pivots
# from fourgp.analysis.support_resistance.pricelevels.visualization.levels_on_candlestick import plot_levels_on_candlestick

from fourgp.utils.make_data import MakeData


def from_config(data: pd.DataFrame, config: dict) -> dict:
    """Get the collection name from the config file and call the appropriate function   

    Args:
        data (pd.DataFrame): data to be used for the collection of levels(support and resistance)
        config (dict): config file with the collection name and the parameters for the collection

    Returns:
        dict: Levels of support and resistance
    """    ""
    if config["support_resistance"]["create_type"] == 'raw':
        levels = raw_levels(data)
        return levels
    elif config["support_resistance"]["create_type"] == 'scoring':
        levels = scoring(data)
        return levels
    elif config["support_resistance"]["create_type"] == 'zigzag':
        levels = zig_zag(data)
        return levels


def from_user_input(data: pd.DataFrame) -> dict:
    """Get the collection name from the user and call the appropriate function

    Args:
        data (pd.DataFrame): The data to be used for the collection of levels(support and resistance)

    Returns:
        dict: The levels of support and resistance
    """
    collect_type = input(
        "Enter type of resistance support calculation type (raw_levels or scoring or zig_zag): ")
    if collect_type == 'raw_levels':
        levels = raw_levels(data)
        return levels
    elif collect_type == 'scoring':
        levels = scoring(data)
        return levels
    elif collect_type == 'zig_zag':
        levels = zig_zag(data)
        return levels
    else:
        print("No such collection Type\n Available types are: raw, scoring, zig_zag")
        print("Please try again")
        return from_user_input(data)


def get_support_resistance(sr_each) -> float:
    sr = []
    for i in sr_each:
        sr += sr_each[i]
    return sr


def from_collection_name(data: pd.DataFrame, collection_name: str) -> dict:
    """Get the collection name from the argument and call the appropriate function

    Args:
        data (pd.DataFrame): The data to be used for the collection of levels(support and resistance)
        collection_name (str): The name of the collection

    Returns:
        dict: The levels of support and resistance
    """
    if collection_name == 'raw':
        levels = raw_levels(data)
        return levels
    elif collection_name == 'scoring':
        levels = scoring(data)
        return levels
    elif collection_name == 'zig_zag':
        levels = zig_zag(data)
        return levels
    else:
        print("No such collection Type\n Available types are: raw, scoring, zig_zag")
        print("Please try again")
        return from_user_input(data)


def clean_levels(levels: dict) -> dict:
    """Clean the levels of support and resistance extract the values itself.

    Args:
        levels (dict): The raw levels of support and resistance

    Returns:
        dict: The cleaned levels of support and resistance(mean all unwanted values,data stuctures are removed)) 
    """
    new = {}
    each_timeframe = []
    for level, value in levels.items():
        if levels[level] is None:
            print(f"No levels found for {level}")
            continue
        each_timeframe.extend(
            int(value[vals]["price"]) for vals in range(len(levels[level]))
        )

        each_timeframe.sort()
        new[level] = each_timeframe
        each_timeframe = []
    del each_timeframe
    return new


def correct_date(df: pd.DataFrame) -> pd.DataFrame:
    """Change the date to the correct format i.e from unix to datetime

    Args:
        df (pd.DataFrame): The dataframe to be corrected

    Returns:
        pd.DataFrame: The dataframe with the correct date format
    """    """"""
    # rename the Date column to DateTime
    df.rename(columns={'Date': 'DateTime'}, inplace=True)
    return df


def main_sr(data: pd.DataFrame, collection_name: str = None, config: dict = None) -> dict:
    """The main function to collect the levels of support and resistance calls the appropriate function based on the collection name

    Args:
        data (pd.DataFrame): The dataframe used for finding the levels of support and resistance
        collection_name (str, optional): The way of calculatind levels. Defaults to None.
        config (dict, optional): The config file containing configurations. Defaults to None.

    Returns:
        dict: The dictionary of levels of support and resistance uncorrected or more bloatware
    """    """"""
    df = correct_date(data.copy())
    if collection_name is not None:
        return from_collection_name(df, collection_name)
    elif config is not None:
        return from_config(df, config)
    else:
        return from_user_input(df)


def main_sr_dict(data: dict, collection_name: str = None, config: dict = None) -> dict:
    """This function calls the main_sr function and returns the levels of support and resistance

    Args:
        data (dict): The dataframe used for finding the levels of support and resistance
        collection_name (str, optional): same as main_sr. Defaults to None.
        config (dict, optional): same as name_sr. Defaults to None.

    Returns:
        dict: The dictionary of levels of support and resistance uncorrected or more bloatware
    """    """"""
    # loop through all the data dictionaries and collect the levels and append them to rs dictionary
    return {
        key: main_sr(value, collection_name, config)
        for key, value in data.items()
    }


def raw_levels(df: pd.DataFrame) -> dict:
    cl = RawPriceClusterLevels(
        None, merge_percent=0.25, use_maximums=True, bars_for_peak=91)
    cl.fit(df)
    # in case you want to display chart
    #plot_levels_on_candlestick(df, levels, only_good=False)
    # plot_levels_on_candlestick(df, levels, only_good=False, path='image.png') # in case you want to save chart to  image
    return cl.levels


def scoring(df: pd.DataFrame) -> dict:
    cl = RawPriceClusterLevels(
        None, merge_percent=0.25, use_maximums=True, bars_for_peak=91)
    cl.fit(df)
    levels = cl.levels
    scorer = TouchScorer()
    scorer.fit(levels, df.copy())

    # print(scorer.scores)
    return scorer.scores


def zig_zag(df: pd.DataFrame) -> dict:
    zig_zag_percent = 0.8

    zl = ZigZagClusterLevels(peak_percent_delta=zig_zag_percent, merge_distance=None,
                             merge_percent=0.1, min_bars_between_peaks=20, peaks='Low')

    zl.fit(df)
    # in case you want to display chart
    #plot_with_pivots(df['Close'].values, zl.levels, zig_zag_percent)
    # plot_with_pivots(df['Close'].values, zl.levels,  zig_zag_percent, path='image.png')  # in case you want to save chart to  image
    return zl.levels


def filter_levels(sr, size):
    # get the levels which are nearer to present level
    pass


def get_nearest_levels(sr_all: dict,timeframe:list, present_value, n,timeframe_str:str):
    # sourcery skip: merge-list-appends-into-extend, remove-unnecessary-else
    # get the levels which are nearer to present level that is nearest to the present level
    # get timeframe
    time=timeframe_from_str(timeframe_str,timeframe_str)
    if sr_all[timeframe_str].__len__() == 0:
        # go to upper timeframe
        # The function has parameter timeframe_num which denotes the number of the timeframe
        try:
            # timeframe_num+=1
            return get_nearest_levels(sr_all, timeframe, present_value, timeframe[time+1])
        except IndexError:
            # implement process to use default values
            logger.error(f"No levels found for {timeframe[timeframe_str]}")
            logger.critical("Exiting")
            exit()
    else:
        sr=sr_all[timeframe_str]
    # sort the sr levels in ascending order
    sr.sort()
    # get the numbers which are nearest to the present value in sr
    # that is by checking the difference between present value and each value in sr
    # return the n nearest values

    # find in between which values in sr the present value lies
    values = []
    for i in range(len(sr)):

        if present_value > sr[i]:
            continue
        # check if the present value lies between the values in sr
        try:
            if present_value < sr[i + 1]:
                values.append(sr[i-2])
                values.append(sr[i-1])
                values.append(sr[i])
                values.append(sr[i + 1])
                break
        except IndexError:
            values.append(sr[i])
            check_get_s_or_r(sr,present_value)
            break
    
    return values
    #     else:
    #         try:
    #             # TODO : should use n to get the nearest n values on each side,n is never used for that
    #             values.append(sr[i-2])
    #             values.append(sr[i-1])
    #             values.append(sr[i])
    #             values.append(sr[i+1])
    #             return values
    #         except IndexError:
    #             logger.warning("IndexError\nContinuing")
    #             continue
    # # If else is not used, the values list will be empty so need to work with different values
    # logger.debug(f"values: {values}")
    # logger.warning("values are empty")
    # # FIXME : this function should return a dictionary of s and r keys
    # return None

def check_get_s_or_r(sr,present_value):
    # after getting the place where the error occured make use of it to return sr values based on it.
    if upper_bound_sr(sr,present_value):
        # add 0.05% to the present value
        return present_value*1.005
    elif lower_bound_sr(sr,present_value):
        # subtract 0.05% from the present value
        return present_value*0.995

def tmp_make(sr_values):
    # this method is for temporary use after the get_nearest_levels method is implemented properly
    # this can be removed
    # this method is used to make the levels of support and resistance dict from sr_values list
    if len(sr_values) == 0:
        return {}
    else:
        return {"support": sr_values[0], "resistance": sr_values[3]}

def upper_bound_sr(sr_values:list,current_price:float):
    # if the current price is the bigger price than any resistance level set resistance level to current price+0.05% of current price
    return max(sr_values) < current_price
def lower_bound_sr(sr_values:list,current_price:float):
    # if the current price is the smaller price than any support level set support level to current price-0.05% of current price
    return min(sr_values) > current_price

def get_greater_sr(sr_values,current_price):
    # This is only called or used when the current price is greater than any resistance level of sr_present,sr_info,sr_fast
    # or when the current price is lesser than any support level of sr_present,sr_info,sr_fast
    # sr_present,sr_info,sr_fast are the levels of support and resistance with first half of the values being the support levels
    # and the second half being the resistance levels
    # The actual thing is that as the lower level sr levels are no sufficient to get the levels we are using the upper level sr levels
    # i.e if the primary_timeframe in config is 5m and informative_timeframe is 1h, then the upper levels of support and resistance are
    # 1d,1w,1m,3m,6m,1y,2y,5y,10y etc.,
    # sr_values contain a dictionary of levels of support and resistance with timeframes as keys
    pass

def timeframe_from_str(timefram:list,timeframe_str):
    # this method is used to get the index of the timeframe in the list of timeframes
    # this is used to get the index of the timeframe in the list of timeframes
    return timefram.index(timeframe_str)