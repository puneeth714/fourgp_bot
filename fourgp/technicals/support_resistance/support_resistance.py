from typing import Any
import pandas as pd

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
            print("No levels found for {}".format(level))
            continue
        for vals in range(len(levels[level])):
            each_timeframe.append(int(value[vals]["price"]))
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

def get_nearest_levels(sr:list, present_value,n):
    # get the levels which are nearer to present level that is nearest to the present level
    
    # sort the sr levels in ascending order
    sr.sort()
    # get the numbers which are nearest to the present value in sr
    # that is by checking the difference between present value and each value in sr
    # return the n nearest values

    # find in between which values in sr the present value lies
    values=[]
    for i in range(len(sr)):
        if present_value > sr[i]:
            continue
        else:
            values.append(sr[i-2])
            values.append(sr[i-1])
            values.append(sr[i])
            values.append(sr[i+1])
            break
    return values