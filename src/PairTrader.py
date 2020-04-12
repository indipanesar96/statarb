from datetime import date, timedelta
from typing import Optional, List

import pandas as pd

from src.Clusterer import Clusterer
from src.Cointegrator2 import Cointegrator2
from src.DataRepository import DataRepository
from src.Filters import Filters
from src.Portfolio import Portfolio
from src.RiskManager import RiskManager
from src.Window import Window


class PairTrader:

    def __init__(self,
                 start_date: date = date(2008, 1, 1),
                 window_length: timedelta = timedelta(days=90),
                 end_date: Optional[date] = None,
                 adf_confidence_level: str = "5%",
                 max_mean_rev_time: float = 15,
                 entry_z: float = 1.5,
                 exit_z: float = 0.5):

        # If end_date is None, run for the entirety of the dataset
        # Window is the lookback period (from t=window_length to t=0 (today) over which we analyse data
        # to inform us on trades to make on t=0 (today).
        # We assume an expanding window for now.

        self.repository = DataRepository()
        initial_window = Window(window_start=start_date,
                                window_length=window_length,
                                repository=self.repository)

        self.start_date: date = start_date
        self.window_length: timedelta = window_length
        self.adf_confidence_level: str = adf_confidence_level  # e.g. "5%" or "1%"
        self.max_mean_rev_time: float = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z

        if end_date is None:
            # Last SNP date, hard coded for now...
            snp_end_date = date(year=2020, month=12, day=31)
            self.end_date = snp_end_date
        else:
            self.end_date = end_date

        self.date_range = [i.date() for i in iter(pd.date_range(start=start_date, end=self.end_date))]

        self.portfolio: Portfolio = Portfolio(100_000, start_date)
        self.current_window: Window = initial_window

        self.history: List[Window] = [initial_window]

        self.today = self.start_date + self.window_length + timedelta(days=1)
        # Days since the start of backtest
        self.days_alive: int = 0
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

    def trade(self):
        for _ in self.date_range:
            print(f"Today is {self.today.strftime('%Y-%m-%d')}")

            clusters = self.clusterer.dbscan(eps=2.5, min_samples=2, window=self.current_window)

            x = self.cointegrator.sig_gen(clusters)

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

        # If it's a weekend, evolve again
        if self.today.weekday() >= 5:
            self.__evolve()


if __name__ == '__main__':
    PairTrader(
        start_date=date(2008, 1, 2),
        window_length=timedelta(days=63),  # 63 trading days per quarter
        end_date=None,
        adf_confidence_level=str("1%"),
        max_mean_rev_time=float(15),
        entry_z=1.5,
        exit_z=0.5
    ).trade()
