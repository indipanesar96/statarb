from datetime import date, timedelta
from typing import Optional, List

import pandas as pd

from src.DataRepository import DataRepository, Universes
from src.util.Features import Features
from src.util.Tickers import Tickers


# from DataRepository import DataRepository, Universes
# from util.Features import Features
# from util.Tickers import Tickers


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

        # After construction of the object we also have self.etf_data nd self.snp_data
        self.__get_window_data(self.window_start, self.window_end)

    def evolve(self):
        # Purely side-effectual; the function just mutates the object
        self.window_length += timedelta(days=1)
        self.window_end += timedelta(days=1)
        self.__get_window_data(self.window_start, self.window_end)
        return self

    def __get_window_data(self, start: date, end: date):
        self.etf_data = self.repository.get(Universes.ETFs, start, end)
        self.snp_data = self.repository.get(Universes.SNP, start, end)

    def get_data(self,
                 universe: Universes,
                 tickers: Optional[List[Tickers]] = None,
                 features: Optional[List[Features]] = None,
                 ):

        '''
        function to get data, with tickers and features specified

        universe: Universe.SNP or Universe.ETFs
        tickers: a list of Tickers or None, if None, return all tickers
        features: a list of Features or None, if None, return all features

        Note it takes lists of Tickers and Features but must be called with:
            - lists of SnpTickers and SnpFeatures
                        OR
            - lists of EtfTickers and EtfFeatures
        This is because:
            - SnpTickers and EtfTickers both inherit from Tickers
                        AND
            - SnpFeaturesand EtfFeatures both inherit from Features

        examples (run under PairTrader.py):

        self.current_window.get_data(Universes.SNP, [SnpTickers.ALLE, SnpTickers.WU])

        2. all tickers' ['ASK', 'BID']
        self.current_window.get_data(Universes.SNP, features=[SnpFeatures.ASK, SnpFeatures.BID])

        3. ['BID','LOW'] for ['FITE','ARKW'], which is from ETF universe
        self.current_window.get_data(Universes.ETFs,
                                    tickers = [EtfTickers.FITE , EtfTickers.ARKW],
                                    features = [EtfFeatures.BID, EtfFeatures.LOW]

        '''

        if tickers is None and features is None:

            if universe == Universes.SNP:
                return self.snp_data
            if universe == Universes.ETFs:
                return self.etf_data

        if universe is Universes.SNP:
            data = self.snp_data
        else:
            data = self.etf_data

        # I will change this to index off the enums instead of strings
        features = [f.value for f in features]
        tickers = [t.value for t in tickers]

        if features is None:
            return data.loc[:, pd.IndexSlice[tickers, :]]
        elif tickers is None:
            return data.loc[:, pd.IndexSlice[:, features]]
        else:
            return data.loc[:, pd.IndexSlice[tickers, features]]
