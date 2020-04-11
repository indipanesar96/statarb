import pandas as pd
import numpy as np
from typing import Optional
import datetime as dt
import datetime as dt
from typing import Optional

import numpy as np
import pandas as pd

from src.Window import Window

import src.util.Tickers as Tickers
import src.util.Features as Features
from from src.DataRepository import Universes
# from Window import Window

class Filters:

    def __init__(self, current_window: Window = None):
        self.current_window = Optional[current_window]
        # historic data from which we calculate the history
        # volumes so we know what constitutes a shock)
        # self.threshold_sigma = threshold_sigma
        # how many stdvs away from mean we classify a shock - to be perturbed

    def apply_volume_shock_filter(self, pairs):
        # pairs structure: List[List[ListTickers.EtfTickers or Tickers.SnpTickers, expecting 2 items]]]
        reduced_pairs = pairs.copy()
        # iter through input pairs to be traded, apply volume shock filter
        #     function call to determine volume shock state or not for each ticker, etf pair
        #             function returns tuple of booleans = states
        #
        #     if states.distinct().size == 2:
        #
        #         remove this key:value paor
        #         dictionary.drop(key:value pair)
        for ticker_pair in pairs.keys():
            first_shock = self.__is_volume_shock(reduced_pairs[0])
            second_shock = self.__is_volume_shock(reduced_pairs[1])
            if first_shock != second_shock:
                reduced_pairs.remove(ticker_pair)
        return reduced_pairs

    def __is_volume_shock(self, ticker):

        # vlume data for ticker : Sr  = self.data[key value pair[key]].volume[date range]
        # # date range is t-375 days to t-125 days but check with paper
        # create a random time series for testing
        # should be replaced by fetching volume data from api
        # volumedf = data_fetching_api(ticker, dt.datetime.today().strftime('%Y-%m-%d'), 250)
        volumedf = pd.DataFrame(np.random.rand(250, 1), columns=['vol'],
                                index=pd.date_range(periods=250,
                                                    end=dt.datetime.today().strftime('%Y-%m-%d')))
        if ticker in Tickers.EtfTickers:
            volumedf = self.current_window.get_data(Universes.ETFs,
                                    tickers = [ticker],
                                    features = [Tickers.BID, EtfFeatures.LOW]

        std = volumedf.vol.std()
        mean = volumedf.vol.mean()
        # create random vol today, should be replaced
        today_vol = np.random.rand()

        # return True or False
        if today_vol > mean + self.threshold_sigma * std:
            return True
        else:
            return False

# if __name = __main
