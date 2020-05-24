from datetime import date, timedelta
from typing import Optional, List

from src.Clusterer import Clusterer
from src.Cointegrator import Cointegrator, AdfPrecisions, CointegratedPair
from src.DataRepository import DataRepository
from src.Filters import Filters
from src.Portfolio import Portfolio
from src.RiskManager import RiskManager
from src.SignalGenerator import SignalGenerator
from src.Window import Window


class PairTrader:

    def __init__(self,
                 backtest_start: date = date(2008, 1, 2),
                 max_active_pairs: float =10,
                 trading_window_length: timedelta = timedelta(days=90),
                 backtest_end: Optional[date] = None,
                 adf_confidence_level: AdfPrecisions = AdfPrecisions.FIVE_PCT,
                 max_mean_rev_time: int = 15,
                 hurst_exp_threshold: float = 0.35,
                 entry_z: float = 1.5,
                 emergency_z: float = 3,
                 exit_z: float = 0.5):
        # If end_date is None, run for the entirety of the dataset
        # Window is the lookback period (from t=window_length to t=0 (today) over which we analyse data
        # to inform us on trades to make on t=0 (today).
        # We assume an expanding window for now.

        self.backtest_start: date = backtest_start
        self.max_active_pairs: float = max_active_pairs
        self.window_length: timedelta = trading_window_length
        self.init_window_length: timedelta = trading_window_length
        self.adf_confidence_level: AdfPrecisions = adf_confidence_level  # e.g. "5%" or "1%"
        self.max_mean_rev_time: int = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z
        self.hurst_exp_threshold: float = hurst_exp_threshold

        # if the pair crosses this boundary, we don't believe their cointegrated anymore
        # - close the position at a loss
        # require: emergency_z > entry_z > exit_z
        self.emergency_z: float = emergency_z

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
        self.days_alive: int = (self.today - self.backtest_start).days #dont know what's goin on here with days_alive
        self.day_count: int = 0
        self.is_window_end: bool = (self.day_count % trading_window_length.days) == 0

        self.clusterer = Clusterer()
        self.cointegrator = Cointegrator(self.repository,
                                         self.adf_confidence_level,
                                         self.max_mean_rev_time,
                                         self.entry_z,
                                         self.exit_z,
                                         initial_window,
                                         self.history[-1],
                                         previous_cointegrated_pairs=[])
        self.risk_manager = RiskManager(self.entry_z, self.exit_z)
        self.filters = Filters()
        self.portfolio: Portfolio = Portfolio(100_000, self.current_window, self.max_active_pairs)
        self.dm = SignalGenerator(self.portfolio,
                                  entry_z,
                                  emergency_z,
                                  exit_z
                                  )

    def trade(self):
        while self.today < self.backtest_end:
            print(f"Today is {self.today.strftime('%Y-%m-%d')}")
            print(self.is_window_end, self.day_count)
            self.is_window_end = (self.day_count % self.init_window_length.days) == 0
            clusters = self.clusterer.dbscan(eps=0.1, min_samples=2, window=self.current_window)
            # print(clusters)

            if self.is_window_end:
                cointegrated_pairs: List[CointegratedPair] = self.cointegrator.generate_pairs(clusters,
                                                                                              self.hurst_exp_threshold)
            else:
                cointegrated_pairs: List[CointegratedPair] = self.cointegrator.get_previous_cointegrated_pairs()

            decisions = self.dm.make_decision(cointegrated_pairs)

            self.portfolio.execute_trades(decisions)

            self.portfolio.update_portfolio()
            self.portfolio.evolve()
            print(self.portfolio.get_port_hist())
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
                f"---- Window start: {self.current_window.window_start}, Window length: {self.current_window.window_length}, Days alive: {self.days_alive}")
            self.__evolve()
        # self.portfolio.summary()
        return

    def __evolve(self):
        # Do all the things to push the window forward to next working day
        # Adjust static parameters
        self.window_length += timedelta(days=1)
        self.days_alive += 1
        self.day_count+=1
        self.today = self.trading_days[-1]
        # Extend window object by one day (expanding)
        self.history.append(self.current_window)
        self.history = self.history[-3:]
        self.current_window = self.current_window.evolve()
        self.trading_days = self.current_window.window_trading_days


if __name__ == '__main__':
    PairTrader(
        # fundamental starts at 2016 2nd quarter
        backtest_start=date(2017, 1, 2),  # must be a trading day
        trading_window_length=timedelta(days=60),  # 63 trading days per quarter
        max_active_pairs=10,
        backtest_end=date(2017, 3, 29),
        adf_confidence_level=AdfPrecisions.ONE_PCT,
        max_mean_rev_time=30,
        entry_z=0.5,
        exit_z=0.1,
        emergency_z=0.8
    ).trade()
