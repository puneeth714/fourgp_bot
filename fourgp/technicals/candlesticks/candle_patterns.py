from fourgp.technicals.candlesticks.all_patterns_talib import all_patterns, all_patterns_pandas_ta
import talib as ta

# CandlePatterns class will take dictionary of pandas dataframes and the pattern names to recognize and how much to trucate the dataframe
# . optionally __filter_data_latest__ can make dataframe truncate to latest  n rows. and get patterns will find patterns in the dataframe available
# in talib or pandas ta(pandas_ta with some modifications).


class CandlePatterns:
    def __init__(self, df_dict: dict, patters: list, trucate: int) -> None:
        """CandlePatterns constructor.

        Args:
            df_dict (dict): The dictionary of dataframes to be used for pattern recognition.
            patters (list): The list of patterns to be recognized.
            trucate (int): To number of rows to be trucated from the dataframe from last i.e 
            latest to be used for pattern recognition.
        """
        self.df_dict = df_dict.copy()
        # self.__filter_data_latest__()
        self.patterns = patters
        self.trucate = trucate

    def __filter_data_latest__(self) -> None:
        """Filter dataframe to latest n rows.
        """
        # get only last 5 values of the dataframe in the given dictionary of dataframes
        for key in self.df_dict:
            self.df_dict[key] = self.df_dict[key].iloc[-int(self.trucate):]

    def available_patterns(self) -> None:
        """Prints the available patterns in talib or pandas ta as mentioned in all_patterns_talib.py.
        """
        # get names of all available patterns
        # print(all_patterns)
        print(all_patterns_pandas_ta)
        print(all_patterns)

    def get_pattern_names(self) -> dict:
        """The get_pattern_names method will go through the dictionary of dataframes and finds the 
        patterns(if any) in the dataframe and adds the pattern name to the dictionary with its value 
        and returns the resultant dataframe of dictionaries.

        Returns:
            dict: The dictionary of dataframes with the pattern names and their values also added to coloumn.
        """        """"""
        # get the patterns which are given in pattern list
        # for vals in self.df:
        #     for pat in self.patterns:
        #         if pat in self.all_patterns:
        #             pat_val=ta.cdl_pattern(self.df_dict[vals]["Open"], self.df_dict[vals]["High"],
        #                            self.df_dict[vals]["Low"], self.df_dict[vals]["Close"], pattern_name=pat)
        #             self.df[pat] = pat_val
        # return self.df

        # Go through the dictionary of dataframes
        for vals in self.df_dict:
            # Go through the list of patterns in the pattern list
            for pat in all_patterns:
                # if the pattern is in the parameter list of patterns
                if pat in self.patterns or self.patterns[0] == "all":
                    # check if the pattern is recognized by talib or pandas ta
                    points = eval("ta.{}".format(pat)+"""(self.df_dict[vals]["Open"].to_numpy(), self.df_dict[vals]["High"].to_numpy(
                    ), self.df_dict[vals]["Low"].to_numpy(), self.df_dict[vals]["Close"].to_numpy())""")
                    # if the pattern is recognized by talib or pandas ta then add the pattern name and its value to the dataframe
                    self.df_dict[vals][pat] = points
                    # print(points)
        return self.df_dict
