from datetime import date, timedelta

from src.DataRepository import DataRepository, DataLocations

import pandas as pd

from typing import Optional, List


class Window:

    def __init__(self,
                 window_start: date,
                 window_length: timedelta,
                 repository: DataRepository):

        self.window_start: date = window_start
        self.window_length: timedelta = window_length
        self.repository: DataRepository = repository

        # Window object contains information about timings for the window as well as SNP and ETF data for that period.
        self.window_end: date = self.window_start + self.window_length

        self.__get_window_data(self.window_start, self.window_end)

    def evolve(self):
        # Purely side-effectual; the function just mutates the object
        self.window_length += timedelta(days=1)
        self.window_end += timedelta(days=1)
        self.__get_window_data(self.window_start, self.window_end)
        return self

    def __get_window_data(self, start: date, end: date):
        self.etf_data = self.repository.get(DataLocations.ETFs, start, end)
        self.snp_data = self.repository.get(DataLocations.SNP, start, end)


    def get_data(self,
                 universe : str, # 'SNP' or 'ETFs'
                 tickers :  Optional[List[str]] = None,
                 features : Optional[List[str]] = None,
                 ):


        '''
        function to get data, with tickers and features specified

        universe: 'SNP' or 'ETFs'
        tickers:  a list of string or None, if None, return all tickers
        features: a list of string or None, if None, return all features

        examples (run under PairTrader.py):

        1. all features for tickers ['ALLE', 'WU']
        data = self.current_window.get_data(universe = 'SNP', tickers = ['ALLE', 'WU'])

        2. all tickers' ['ASK', 'BID']
        data = self.current_window.get_data(universe = 'SNP', features = ['ASK', 'BID'])

        3. ['BID','LOW'] for ['FITE','ARKW'], which is from ETF universe
        data = self.current_window.get_data(universe='ETFs', tickers = ['FITE','ARKW'], features = ['BID','LOW'])

        ########################################################################

        note: you can use following to get available tickers and features

        from src.DataRepository import DataRepository, DataLocations

        # all available features for ETFs
        self.current_window.repository.features[DataLocations.ETFs]

        # all available tickers for SNP
        self.current_window.repository.tickers[DataLocations.SNP]

        '''

        if universe =='SNP':
            data = self.repository.all_data[DataLocations.SNP]
        elif universe == 'ETFs':
            data = self.repository.all_data[DataLocations.ETFs]
        else:
            print ('wrong security universe!')
            return None

        data = data.loc[self.window_start : self.window_end,:]

        if (tickers == None) & (features == None):
            return data
        elif (features == None):
            return data.loc[:, pd.IndexSlice[ tickers , :] ]
        elif (tickers == None):
            return data.loc[:, pd.IndexSlice[:, features]]
        else:
            return data.loc[:, pd.IndexSlice[ tickers , features ]]
