# 1. consider a period to assess volume shock , consider cases where it shocks before but not today

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
from src.util.Features import Features
from src.DataRepository import Universes
from src.Cointegrator import CointegratedPair
# from Window import Window

class Filters:

    def __init__(self, threshold_sigma = 1):
        self.current_window = None
        # historic data from which we calculate the history
        # volumes so we know what constitutes a shock)
        self.threshold_sigma = threshold_sigma
        # how many stdvs away from mean we classify a shock - to be perturbed

    def run_volume_shock_filter(self, pairs, current_window):
        # pairs structure: List[List[ListTickers.EtfTickers or Tickers.SnpTickers, expecting 2 items]]]
        self.current_window = current_window
        reduced_pairs = pairs.copy()
        # iter through input pairs to be traded, apply volume shock filter
        #     function call to determine volume shock state or not for each ticker, etf pair
        #             function returns tuple of booleans = states
        #
        #     if states.distinct().size == 2:
        #
        #         remove this key:value paor
        #         dictionary.drop(key:value pair)
        for pair in pairs:
            first_shock = self.__is_volume_shock(pair[0][0])
            second_shock = self.__is_volume_shock(pair[0][1])
            if first_shock != second_shock:
                reduced_pairs.remove(pair)
        return reduced_pairs

    def __is_volume_shock(self, ticker):

        # vlume data for ticker : Sr  = self.data[key value pair[key]].volume[date range]
        # # date range is t-375 days to t-125 days but check with paper
        # create a random time series for testing
        # should be replaced by fetching volume data from api
        # volumedf = data_fetching_api(ticker, dt.datetime.today().strftime('%Y-%m-%d'), 250)
        '''
        pd.DataFrame(np.random.rand(250, 1), columns=['vol'],
                                index=pd.date_range(periods=250,
                                                    end=dt.datetime.today().strftime('%Y-%m-%d')))
        '''
        if ticker in Tickers.EtfTickers:
            volume = self.current_window.get_data(Universes.ETFs,
                                    tickers = [ticker],
                                    features = [Features.VOLUME])
        elif ticker in Tickers.SnpTickers:
            volume = self.current_window.get_data(Universes.SNP,
                                    tickers = [ticker],
                                    features = [Features.VOLUME])


        hist_vol = volume[:-1]
        today_vol = volume[-1:]
        std = hist_vol.std()
        mean = hist_vol.mean()
        # create random vol today, should be replaced

        # return True or False
        shock = (today_vol > mean + self.threshold_sigma * std).values[0][0]
        if shock:
            return True
        else:
            return False

from src.util.Tickers import SnpTickers
from src.DataRepository import DataRepository
from datetime import date, timedelta

if __name__ == '__main__':
    win = Window(window_start=date(2008, 1, 2),
                 trading_win_len=timedelta(days=90),
                 repository=DataRepository())

    test_input = [
        CointegratedPair(pair=(SnpTickers.CRM, SnpTickers.WU),
                         mu_x_ann=0.1,
                         sigma_x_ann=0.3,
                         scaled_beta=1.2,
                         hl=7.5,
                         ou_mean=-0.017,
                         ou_std=0.043,
                         ou_diffusion_v=0.70,
                         recent_dev=0.071,
                         recent_dev_scaled=2.05),

        CointegratedPair(pair=(SnpTickers.ABC, SnpTickers.ABT),
                         mu_x_ann=0.1,
                         sigma_x_ann=0.3,
                         scaled_beta=0.8,
                         hl=7.5,
                         ou_mean=-0.017,
                         ou_std=0.043,
                         ou_diffusion_v=0.70,
                         recent_dev=- 0.071,
                         recent_dev_scaled=-2.05)
    ]

    ft = Filters()
    test_result = ft.run_volume_shock_filter(test_input, current_window = win)