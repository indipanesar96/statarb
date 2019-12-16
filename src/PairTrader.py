from typing import Tuple, Dict
from src.DataRepository import DataRepository
from src.Cointegrator import Cointegrator
from src.Clustering import Clustering
from src.Plotter import Plotter
from src.Filters import Filters
from src.Executor import Executor
from src.RiskManager import RiskManager
from pandas import DataFrame as Df
from pandas import Series as Se


class PairTrader:

    def __init__(self,
                 window_size: int = 60,
                 open_thresh: float = 1.0,
                 close_thresh: float = 2.0,
                 holding_period: int = 15,
                 sim_days: int = None) -> object:
        '''
        :param window_size: the size of the window over which we run clustering and
                            cointegration analysis on to inform the trader on decisions
        :param open_thresh: how many standard deviations away from mean the cointegation signal needs to be before
                            deciding to open a long/short pair position (in magnitude)
        :param close_thresh: how many standard deviations away from mean the cointegation signal needs to be before
                            deciding to close a long/short pair position (in magnitude)
        :param sim_days: The total length of the simulation/backtesting period. If None, the trader will trade over the
                        full extent of the dataset imported

                        #whats max trading threshold per day? how do we start the portfolio??? all cash?
        '''
        self.window_size: int = window_size
        self.open_thresh: float = open_thresh
        self.close_thresh: float = close_thresh
        self.sim_days: float = sim_days
        self.portfolio: Df = Df()

    def trade(self):
        repository = DataRepository()
        t_minus_one_data: Se = repository.pull_latest()
        executor = Executor(t_minus_one_data)
        cointegrator = Cointegrator(executor)
        clusterer = Clustering()
        risk_manager = RiskManager()
        filterer = Filters()
        plotter = Plotter()

        self.portfolio = repository.pull_initial()

        def evolve(day_number: int) -> Df:
            if day_number != 0:
                # all other stop losses here / term limit checks etc
                self.portfolio = cointegrator.check_holdings(self.portfolio)
                day_open_risk_metrics = risk_manager.current_exposure(self.portfolio)
            else:
                day_open_risk_metrics = None

            clustering_results: Dict[int, Tuple[str]] = clusterer.dbscan()

            price_data_for_cointegration = repository.get_data_for_coint()

            pairs, reversions = cointegrator.run_cointegration_analysis(clustering_results,
                                                                        price_data_for_cointegration)

            reduced_pairs, reduced_reversions = filterer.apply_volume_shock_filter(pairs, reversions)

            self.portfolio = executor.open_positions(reduced_pairs, reduced_reversions, day_open_risk_metrics)

            post_trade_risk_metrics = risk_manager.current_exposure(self.portfolio)

            plotter.plot(self.portfolio, post_trade_risk_metrics)

            return self.portfolio

        # the portfolio at each timestep
        holdings_series = list(map(lambda n: evolve(n), (i for i in self.sim_days)))

        pass


if __name__ == '__main__':
    # feeling out the parameter space
    PairTrader(window_size=60,
               open_thresh=0.1,
               close_thresh=1.8,
               sim_days=60).trade()
    PairTrader(window_size=60,
               open_thresh=0.2,
               close_thresh=1.7,
               holding_period=10,
               sim_days=None).trade()

    # with this design pattern we can instantiate multiple PairTraders (ie multiple backtest in sequence)
    # with different parameters and attributes, to compare the results as the system gets more complicated
    # it becomes a 'complex system' c.f. https://en.wikipedia.org/wiki/Complex_system
    # we build the system, poke at it with different initial parameters and see how that affects the output it spits out
