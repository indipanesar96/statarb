import datetime
from datetime import date, timedelta
from typing import Optional, List

import pandas as pd
from pandas import DataFrame

from src.Cointegrator import Cointegrator
from src.DataRepository import DataRepository, Universes
from src.Clusterer import Clusterer
from src.Filters import Filters
from src.Window import Window
# from Cointegrator import Cointegrator
# from DataRepository import DataRepository, Universes
# from Clusterer import Clusterer
# from Filters import Filters
# from Window import Window


# 1. Features common to ETF and SNP for clustering -? calls to yfinance
# 2. cluster on stock stock pair if not


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
        # Window is the lookback period (from t=-window_length-1 to t=-1 (yesterday) over which we analyse data
        # to inform us on trades to make on t=0 (today). We assume an expanding window for now.

        self.repository = DataRepository()
        initial_window = Window(window_start=start_date,
                                window_length=window_length,
                                repository=self.repository)

        self.start_date: date = start_date
        self.window_length: timedelta = window_length
        self.adf_confidence_level: str = adf_confidence_level  #specify as string percentage like "5%" or "1%"
        self.max_mean_rev_time: float = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z

        if end_date is None:
            # Last SNP date, hard coded for now...
            self.end_date = date(year=2020, month=12, day=31)
        else:
            self.end_date = end_date

        self.date_range = [i.date() for i in iter(pd.date_range(start=start_date, end=self.end_date))]

        # Portfolio might need to be its own object later, cross that bridge when we come to it
        self.portfolio: Optional[DataFrame] = None
        self.current_window: Window = initial_window

        # Is this required? Isn't history just all data since self.start_date? (for an expanding window)
        # Indi thinking to himself

        self.history: List[Window] = [initial_window]

        self.today = self.start_date + self.window_length + timedelta(days=1)
        snp_end_date = date(year=2020, month=12, day=31)
        # Days since the start of backtest
        self.days_alive: int = 0

        ### Jay Part
        self.clusterer = Clusterer()
        self.clusterer.dbscan(eps=2.0, min_samples=2, window=initial_window) # this uses stimulated data for testing purpose
        #self.clusterer.kmeans(self.clusterer.n_clusters) # this uses stimulated data for testing purpose
        print(self.clusterer.dbscan_labels)
        #print(self.clusterer.kmeans_labels)
        ###

        self.cointegrator = Cointegrator(self.repository, self.adf_confidence_level, self.max_mean_rev_time, self.entry_z, self.exit_z)
        self.filters = Filters()

    def trade(self):
        for _ in self.date_range:
            print(f"Today is {self.today.strftime('%Y-%m-%d')}")

            x=10

            # Using DBScan for now, ensemble later
            # cluster_results = self.clusterer.DBScan(self.current_window)

            # Take cluster results and pass into Cointegrator and return signals

            # Take cointegrated signals and pass into Filter = filtered signal
            # use something like: signal = self.cointegrator.run_cointegrator(cluster_results)


            # Take filtered signal

            # roll forward/expand window

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
    trader  = PairTrader(
        start_date=date(2008, 1, 1),
        window_length=timedelta(days=90),
        end_date=None,
        adf_confidence_level = str("1%"),
        max_mean_rev_time = float(15),
        entry_z = 1.5,
        exit_z = 0.5
    )
