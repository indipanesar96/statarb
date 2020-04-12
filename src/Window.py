from datetime import date, timedelta
from typing import Optional, List

import pandas as pd
from pandas import DataFrame

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
        # After construction of the object we also have self.etf_data nd self.snp_data and the live tickers for each

        self.window_trading_days = self.__get_weekdays_for_window(start_date=window_start, window_size=window_length)
        self.window_end: date = self.window_trading_days[-1]
        self.__get_window_data(self.window_trading_days)

    def __get_weekdays_for_window(self, start_date: date, window_size: timedelta) -> List[date]:
        # Ensures we have a window with window__size trading days
        weekdays: List[date] = []
        counter = 0
        while len(weekdays) < window_size.days:
            current_weekday = start_date + timedelta(days=counter)
            # 0 = Monday, 6 = Sunday
            if current_weekday.weekday() < 5:
                weekdays.append(current_weekday)
            counter += 1
        return weekdays

    def evolve(self):
        # Purely side-effectual; the function just mutates the object
        self.window_length += timedelta(days=1)
        self.window_end += timedelta(days=1)
        self.__get_window_data(self.window_trading_days)
        return self

    def __get_window_data(self, trading_dates: List[date]):
        etf_live_tickers, etf_data = self.repository.get(Universes.ETFs, trading_dates)
        snp_live_tickers, snp_data = self.repository.get(Universes.SNP, trading_dates)

        self.etf_data = etf_data
        self.snp_data = snp_data

        self.etf_live_tickers = etf_live_tickers
        self.snp_live_tickers = snp_live_tickers

    def get_data(self,
                 universe: Universes,
                 tickers: Optional[List[Tickers]] = None,
                 features: Optional[List[Features]] = None,
                 ) -> DataFrame:

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
            - SnpFeatures and EtfFeatures both inherit from Features

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
            if universe is Universes.SNP:
                return self.snp_data
            if universe is Universes.ETFs:
                return self.etf_data

        if universe is Universes.SNP:
            data = self.snp_data
        else:
            data = self.etf_data

        if tickers is not None and features is None:

            return data.loc[:, pd.IndexSlice[tickers, :]]

        elif tickers is None and features is not None:

            return data.loc[:, pd.IndexSlice[:, features]]

        elif tickers is not None and features is not None:

            return data.loc[:, pd.IndexSlice[tickers, features]]
