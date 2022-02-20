import numpy
from zigzag import *
import pandas as pd


def zig_zag_binary(data: pd.DataFrame, config: dict) -> numpy:
    # Find the zig zag binary for the data in ohcl format
    numpy_data = pandas_to_numpy(data, "Close")
    return peak_valley_pivots(numpy_data, 0.01, -0.01)
    # peak_valley_poivot()


def pandas_to_numpy(data: pd.DataFrame, part: str):
    return data[part].to_numpy()


def zigzag(df, depth, deviation, backstep, pip_size):
    i = depth

    zigzag_buffer = pd.Series(
        0*df['Close'], name='ZigZag_' + str(depth) + "_" + str(deviation) + "_" + str(backstep))
    high_buffer = pd.Series(0*df['Close'])
    low_buffer = pd.Series(0*df['Close'])

    curlow = 0
    curhigh = 0
    lasthigh = 0
    lastlow = 0

    whatlookfor = 0

    lows = pd.Series(df['Low'].rolling(depth).min())
    highs = pd.Series(df['High'].rolling(depth).max())

    while i + 1 <= df.index[-1]:
        extrem_um = lows[i]
        if extrem_um == lastlow:
            extrem_um = 0
        else:
            lastlow = extrem_um
            if df.at[i, 'Low']-extrem_um > deviation*pip_size:
                extrem_um = 0
            else:
                for back in range(1, backstep + 1):
                    pos = i-back
                    if low_buffer[pos] != 0 and low_buffer[pos] > extrem_um:
                        low_buffer[pos] = 0

        low_buffer[i] = extrem_um if df.at[i, 'Low'] == extrem_um else 0
        extrem_um = highs[i]
        if extrem_um == lasthigh:
            extrem_um = 0
        else:
            lasthigh = extrem_um
            if extrem_um - df.at[i, 'High'] > deviation*pip_size:
                extrem_um = 0
            else:
                for back in range(1, backstep + 1):
                    pos = i - back
                    if high_buffer[pos] != 0 and high_buffer[pos] < extrem_um:
                        high_buffer[pos] = 0

        high_buffer[i] = extrem_um if df.at[i, 'High'] == extrem_um else 0
        i = i + 1

    lastlow = 0
    lasthigh = 0

    i = depth

    while i + 1 <= df.index[-1]:
        if whatlookfor == 0:
            if lastlow == 0 and lasthigh == 0:
                if high_buffer[i] != 0:
                    lasthigh = df.at[i, 'High']
                    lasthighpos = i
                    whatlookfor = -1
                    zigzag_buffer[i] = lasthigh
                if low_buffer[i] != 0:
                    lastlow = df.at[i, 'Low']
                    lastlowpos = i
                    whatlookfor = 1
                    zigzag_buffer[i] = lastlow
        elif whatlookfor == 1:
            if low_buffer[i] != 0 and low_buffer[i] < lastlow and high_buffer[i] == 0:
                zigzag_buffer[lastlowpos] = 0
                lastlowpos = i
                lastlow = low_buffer[i]
                zigzag_buffer[i] = lastlow
            if high_buffer[i] != 0 and low_buffer[i] == 0:
                lasthigh = high_buffer[i]
                lasthighpos = i
                zigzag_buffer[i] = lasthigh
                whatlookfor = -1
        elif whatlookfor == -1:
            if high_buffer[i] != 0 and high_buffer[i] > lasthigh and low_buffer[i] == 0:
                zigzag_buffer[lasthighpos] = 0
                lasthighpos = i
                lasthigh = high_buffer[i]
                zigzag_buffer[i] = lasthigh
            if low_buffer[i] != 0 and high_buffer[i] == 0:
                lastlow = low_buffer[i]
                lastlowpos = i
                zigzag_buffer[i] = lastlow
                whatlookfor = 1

        i = i + 1

    df = df.join(zigzag_buffer)
    return df["ZigZag_" + str(depth) + "_" + str(deviation) + "_" + str(backstep)].values
