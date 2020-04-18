from datetime import date, timedelta
from typing import Optional, List

import pandas as pd

from src.Clusterer import Clusterer
from src.Cointegrator2 import Cointegrator2, AdfPrecisions, CointegratedPair
from src.DataRepository import DataRepository
from src.Filters import Filters
from src.Portfolio import Portfolio
from src.RiskManager import RiskManager
from src.Window import Window


class PairTrader:

    def __init__(self,
                 backtest_start: date = date(2008, 1, 2),
                 trading_window_length: timedelta = timedelta(days=90),
                 backtest_end: Optional[date] = None,
                 adf_confidence_level: AdfPrecisions = AdfPrecisions.FIVE_PCT,
                 max_mean_rev_time: int = 15,
                 entry_z: float = 1.5,
                 exit_z: float = 0.5):

        # If end_date is None, run for the entirety of the dataset
        # Window is the lookback period (from t=window_length to t=0 (today) over which we analyse data
        # to inform us on trades to make on t=0 (today).
        # We assume an expanding window for now.

        self.backtest_start: date = backtest_start
        self.window_length: timedelta = trading_window_length
        self.adf_confidence_level: AdfPrecisions = adf_confidence_level  # e.g. "5%" or "1%"
        self.max_mean_rev_time: int = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z

        # Last SNP date, hard coded for now...
        self.backtest_end = date(year=2020, month=12, day=31) if backtest_end is None else backtest_end

        self.repository = DataRepository()
        initial_window = Window(window_start=backtest_start,
                                trading_win_len=trading_window_length,
                                repository=self.repository)

        self.current_window: Window = initial_window
        self.history: List[Window] = [initial_window]

        self.trading_days = initial_window.window_trading_days
        self.today = self.trading_days[-1]
        self.days_alive: int = (self.today - self.backtest_start).days

        self.clusterer = Clusterer()
        self.cointegrator = Cointegrator2(self.repository,
                                          self.adf_confidence_level,
                                          self.max_mean_rev_time,
                                          self.entry_z,
                                          self.exit_z,
                                          initial_window,
                                          self.history[-1])
        self.risk_manager = RiskManager()
        self.filters = Filters()
        self.portfolio: Portfolio = Portfolio(100_000, backtest_start)

    def trade(self):
        while self.today < self.backtest_end:
            print(f"Today is {self.today.strftime('%Y-%m-%d')}")

            clusters = self.clusterer.dbscan(eps=2.5, min_samples=2, window=self.current_window)

            cointegrated_pairs: List[CointegratedPair] = self.cointegrator.generate_pairs(clusters)


            # Take cointegrated signals and pass into Filter = filtered signal
            # should return pairs of cointegrated stocks, with their weightings

            # Take filtered signal
            # input datatype = output datatype

            # RiskManager
            # input = output from filterer
            # Can we afford it? do we have enough cash? checkd exposure etc, VaR within limits etc?
            # if ok, pass any remaining pairs to executor

            # Executor,
            # opens positions passed to it form filterer
            # executor needs to update the portfolio

            print(
                f"Window start: {self.current_window.window_start}, Window length: {self.current_window.window_length}, Days alive: {self.days_alive}")
            self.__evolve()

    def __evolve(self):
        # Do all the things to push the window forward to next working day
        # Adjust static parameters
        self.today += timedelta(days=1)
        self.window_length += timedelta(days=1)
        self.days_alive += 1
        # Extend window object by one day (expanding)
        self.history.append(self.current_window)
        self.history = self.history[-3:]

        self.current_window = self.current_window.evolve()


if __name__ == '__main__':
    PairTrader(
        backtest_start=date(2008, 1, 2), # must be a trading day
        trading_window_length=timedelta(days=10),  # 63 trading days per quarter
        backtest_end=None,
        adf_confidence_level=AdfPrecisions.ONE_PCT,
        max_mean_rev_time=15,
        entry_z=1.5,
        exit_z=0.5
    ).trade()
