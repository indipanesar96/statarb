import sys
from datetime import date, timedelta
from typing import List, Optional

import pandas as pd
from pandas import DataFrame

from src.DataRepository import DataRepository, Universes
from src.util.Features import Features
from src.util.Tickers import Tickers


class Window:

    def __init__(self,
                 window_start: date,
                 trading_win_len: timedelta,
                 repository: DataRepository):

        # Window object contains information about timings for the window as well as SNP and ETF data for that period.
        # After construction of the object we also have self.etf_data nd self.snp_data and the live tickers for each

        self.window_start: date = window_start
        self.window_length: timedelta = trading_win_len
        self.repository: DataRepository = repository

        self.window_end = self.__get_nth_working_day_ahead(window_start, trading_win_len.days - 1)
        self.lookback_win_dates = self.__get_window_trading_days(window_start, trading_win_len)
        self.__update_window_data(self.lookback_win_dates)

    def __get_window_trading_days(self, window_start: date, window_length: timedelta):

        start_idx = None
        for idx, d in enumerate(self.repository.all_dates):
            if self.repository.check_date_equality(window_start, d):
                start_idx = idx
                break

        if start_idx is None:
            print("The window start date was not in the list if all dates.")
            print("Ensure backtest is started with a day that is in the datset.")
            sys.exit()

        window_trading_days = self.repository.all_dates[start_idx: start_idx + window_length.days]
        return window_trading_days

    def __update_window_data(self, trading_dates_to_get_data_for: List[date]):

        if self.repository.all_data[Universes.SNP] is None:
            # ie need to load the new window from disk for first time

            self.repository.get(Universes.ETFs, trading_dates_to_get_data_for)
            self.repository.get(Universes.SNP, trading_dates_to_get_data_for)

        if self.window_end > max(self.repository.all_data[Universes.SNP].index):
            # ie need to load the new window from disk

            read_ahead_win_start = self.__get_nth_working_day_ahead(max(self.repository.all_data[Universes.SNP].index),
                                                                    1)
            look_forward_win_dates = self.__get_window_trading_days(read_ahead_win_start, self.window_length)

            self.repository.get(Universes.ETFs, look_forward_win_dates)
            self.repository.get(Universes.SNP, look_forward_win_dates)

        lookback_temp_etf_data = self.repository.all_data[Universes.ETFs].loc[trading_dates_to_get_data_for]
        lookback_temp_snp_data = self.repository.all_data[Universes.SNP].loc[trading_dates_to_get_data_for]

        _, self.etf_data = self.repository.remove_dead_tickers(Universes.ETFs, lookback_temp_etf_data)
        _, self.snp_data = self.repository.remove_dead_tickers(Universes.SNP, lookback_temp_snp_data)

    def roll_forward_one_day(self) -> None:

        self.window_start = self.__get_nth_working_day_ahead(self.window_start, 1)
        self.window_end = self.__get_nth_working_day_ahead(self.window_end, 1)

        self.lookback_win_dates = self.__get_window_trading_days(self.window_start, self.window_length)
        # last window trading date should be today + 1 because today gets updated after this function gets called
        self.__update_window_data(self.lookback_win_dates)

    def __get_nth_working_day_ahead(self, target: date, n: int):
        for idx, d in enumerate(self.repository.all_dates):
            if self.repository.check_date_equality(d, target):
                return self.repository.all_dates[idx + n]

        print("The window start date was not in the list if all dates.")
        print("Ensure backtest is started with a day that is in the datset.")

    def get_data(self,
                 universe: Universes,
                 tickers: Optional[List[Tickers]] = None,
                 features: Optional[List[Features]] = None) -> DataFrame:

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

    def get_fundamental(self):
        return self.repository.get_fundamental(self.window_end)


if __name__ == "__main__":
    win_length = timedelta(days=5)
    today = date(year=2008, month=1, day=2)
    win = Window(window_start=today,
                 trading_win_len=win_length,
                 repository=DataRepository(win_length))

    days_rolled_forward = 0
    while days_rolled_forward <= 2 * win_length.days:
        win.roll_forward_one_day()

        if days_rolled_forward == 10:
            y = 10
        elif days_rolled_forward == 11:
            z = 10

        days_rolled_forward += 1
