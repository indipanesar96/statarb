from pandas import Series as Sr
import pandas as pd
import numpy as np
import datetime as dt
from src.Window import Window

class Filters:

    def __init__(self, current_window : Window):
        self.current_window = current_window
        # historic data from which we calculate the history
        # volumes so we know what constitutes a shock)
        # self.threshold_sigma = threshold_sigma
        #how many stdvs away from mean we classify a shock - to be perturbed

    def apply_volume_shock_filter(self, pairs):
        # pairs structure: {[ticker, ETFTicker]: [size of short, size of long]}
        reduced_pairs =pairs.copy()
        # iter through input pairs to be traded, apply volume shock filter
        #     function call to determine volume shock state or not for each ticker, etf pair
        #             function returns tuple of booleans = states
        #
        #     if states.distinct().size == 2:
        #
        #         remove this key:value paor
        #         dictionary.drop(key:value pair)
        for ticker_pair in pairs.keys():
            stock_shock = self.__is_volume_shock(reduced_pairs[0])
            etf_shock = self.__is_volume_shock(reduced_pairs[1])
            if stock_shock != etf_shock:
                del reduced_pairs[ticker_pair]
        return reduced_pairs


    def __is_volume_shock(self, ticker):

        # vlume data for ticker : Sr  = self.data[key value pair[key]].volume[date range]
        # # date range is t-375 days to t-125 days but check with paper
        # create a random time series for testing
        # should be replaced by fetching volume data from api
        # volumedf = data_fetching_api(ticker, dt.datetime.today().strftime('%Y-%m-%d'), 250)
        volumedf = pd.DataFrame(np.random.rand(250, 1), columns=['vol'],
                                index = pd.date_range(periods = 250,
                                                      end = dt.datetime.today().strftime('%Y-%m-%d') ))
        std = volumedf.vol.std()
        mean = volumedf.vol.mean()
        # create random vol today, should be replaced
        today_vol = np.random.rand()

        # return True or False
        if today_vol > mean + self.threshold_sigma * std:
            return True
        else:
            return False

