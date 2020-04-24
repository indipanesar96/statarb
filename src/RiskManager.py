import numpy as np

from src.DataRepository import Universes
from src.Window import Window
from src.util.Features import Features
from src.util.Tickers import SnpTickers


class RiskManager:

    # input:
    #   existing portfolio: {pairs: long/short volume}
    #   new recommended arbitragable pairs {pairs: long/short volume}

    # object:
    #   assume all pairs have equal expected return
    #   minimize portfolio variance

    # output:
    #   new portfolio

    # should consider turnover - transaction cost
    #   a heavier weight on existing port, lighter weight on new recommendation

    def __init__(self):
        self.current_window = None

    def current_exposure(self, port_current_open_positions):
        pass

    def run_risk_manager(self, cointegrated_pairs, current_window):
        self.current_window = current_window
        pairs_cov, pairs_expected_return = self.__cov_mu(cointegrated_pairs)
        tg_port = self.__mean_variance_optimizer(cov_matrix=pairs_cov, expected_return=pairs_expected_return)
        return tg_port

    def __port_ts(self, pair):
        # assume always trading stock-stock pair
        # get pair's time series of last price
        pair_ts = self.current_window.get_data(universe=Universes.SNP, tickers=[pair[0][0], pair[0][1]],
                                               features=Features.CLOSE)
        port_ts = pair_ts.iloc[:, 0] * pair[1][0] + pair_ts.iloc[:, 1] * pair[1][1]
        port_ts = port_ts.to_frame()
        port_ts.columns = [pair[0][0].value + ' - ' + pair[0][1].value]
        return port_ts

    def __cov_mu(self, pairs):
        pair_price_df_started = False
        pair_expected_return = []
        for pair in pairs:
            if (pair[1][0] == 0) & (pair[1][1] == 0):
                continue
            if not pair_price_df_started:
                pairs_price_df = self.__port_ts(pair)
                pair_price_df_started = True
            else:
                this_port = self.__port_ts(pair)
                pairs_price_df = pairs_price_df.join(this_port)

            pair_expected_return.append(pair[1][3])
        pair_expected_return = np.matrix(pair_expected_return).transpose()
        return pairs_price_df.cov(), pair_expected_return

    def __mean_variance_optimizer(self, cov_matrix, expected_return):
        cov_matrix_inv = np.linalg.inv(cov_matrix.values)
        weight = cov_matrix_inv.dot(expected_return)
        scale = weight.sum()
        weight = weight / scale
        return weight


from datetime import date, timedelta
from src.DataRepository import DataRepository

if __name__ == '__main__':
    win = Window(window_start=date(2008, 1, 2),
                 trading_win_len=timedelta(days=90),
                 repository=DataRepository())

    test_input = [
        [
            [SnpTickers.CRM, SnpTickers.WU],
            [1, -1.5,  # long short size
             None,  # self.invested
             0.1]  # expected return
        ],

        [
            [SnpTickers.ABC, SnpTickers.ABT],
            [-0.5, 1,
             None,
             0.15]
        ]
    ]

    rm = RiskManager()
    rm.run_risk_manager(cointegrated_pairs=test_input, current_window=win)
