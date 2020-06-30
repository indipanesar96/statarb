import numpy as np

from datetime import date, timedelta
from src.DataRepository import DataRepository
from src.DataRepository import Universes
from src.Window import Window
from src.util.Features import Features
from src.util.Tickers import SnpTickers
from src.util.ExpectedReturner import expected_returner
from enum import Enum, unique
from src.Cointegrator import CointegratedPair


@unique
class TradeDirection(Enum):
    LONG = 'LONG'
    SHORT = 'SHORT'


class tradable_pair:
    def __init__(self, cointegrated_pair, direction):
        self.pair: CointegratedPair = cointegrated_pair
        self.direction: TradeDirection = direction


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

    def __init__(self, entry_z, exit_z):
        self.current_window = None
        self.entry_z = entry_z
        self.exit_z = exit_z

    def current_exposure(self, port_current_open_positions):
        pass

    def run_risk_manager(self, cointegrated_pairs, current_window):
        self.current_window = current_window
        tradable_pairs = []
        for pair in cointegrated_pairs:
            if pair.recent_dev_scaled > self.entry_z:
                # long x short y
                tradable_pairs.append(tradable_pair(cointegrated_pair=pair, direction=TradeDirection.LONG))
            elif pair.recent_dev_scaled < -self.entry_z:
                # short x long y
                tradable_pairs.append(tradable_pair(cointegrated_pair=pair, direction=TradeDirection.SHORT))
        pairs_cov = self.__cov(tradable_pairs)
        pairs_mu = self.__mu(tradable_pairs)
        tg_port = self.__mean_variance_optimizer(cov_matrix=pairs_cov, expected_return=pairs_mu)
        return tg_port

    def __get_close(self, pair, last=False):
        pair_ts = self.current_window.get_data(universe=Universes.SNP, tickers=[pair.pair[0], pair.pair[1]],
                                               features=Features.CLOSE)
        if last:
            xf = pair_ts.iloc[-1, 0]
            yf = pair_ts.iloc[-1, 1]
            return xf, yf
        else:
            return pair_ts

    # model look ahead vol with stats from cointegrator - OU std......
    #

    def __port_ts(self, pair, direction):
        # assume always trading stock-stock pair
        # get pair's time series of last price
        pair_ts = self.__get_close(pair=pair)
        if direction == TradeDirection.LONG:
            port_ts = pair_ts.iloc[:, 0] * pair.scaled_beta - pair_ts.iloc[:, 1]
        elif direction == TradeDirection.SHORT:
            port_ts = - pair_ts.iloc[:, 0] * pair.scaled_beta + pair_ts.iloc[:, 1]
        port_ts = port_ts.to_frame()
        port_ts.columns = [pair.pair[0].value + ' - ' + pair.pair[1].value]
        return port_ts

    def __cov(self, tradable_pairs):
        pair_price_df_started = False
        for tradable_pair in tradable_pairs:
            if not pair_price_df_started:
                pairs_price_df = self.__port_ts(tradable_pair.pair, tradable_pair.direction)
                pair_price_df_started = True
            else:
                this_port = self.__port_ts(tradable_pair.pair, tradable_pair.direction)
                pairs_price_df = pairs_price_df.join(this_port)
        return pairs_price_df.cov()

    def __mu(self, tradable_pairs):
        pair_expected_return = []
        for tradable_pair in tradable_pairs:
            xf, yf = self.__get_close(pair=tradable_pair.pair, last=True)
            mu = expected_returner(cointegrated_pair=tradable_pair.pair, xf=xf, yf=yf)
            pair_expected_return.append(mu)
        return pair_expected_return

    def __mean_variance_optimizer(self, cov_matrix, expected_return):
        cov_matrix_inv = np.linalg.inv(cov_matrix.values)
        weight = cov_matrix_inv.dot(expected_return)
        scale = weight.sum()
        weight = weight / scale
        return weight[:, 0]


if __name__ == '__main__':
    win = Window(window_start=date(2008, 1, 2),
                 trading_win_len=timedelta(days=90),
                 repository=DataRepository())

    test_input = [
        CointegratedPair(pair=(SnpTickers.CRM, SnpTickers.WU),
                         mu_x_ann=0.1,
                         sigma_x_ann=0.3,
                         scaled_beta=1.2,
                         hl=7.5,
                         ou_mean=-0.017,
                         ou_std=0.043,
                         ou_diffusion_v=0.70,
                         recent_dev=0.071,
                         recent_dev_scaled=2.05),

        CointegratedPair(pair=(SnpTickers.ABC, SnpTickers.ABT),
                         mu_x_ann=0.1,
                         sigma_x_ann=0.3,
                         scaled_beta=0.8,
                         hl=7.5,
                         ou_mean=-0.017,
                         ou_std=0.043,
                         ou_diffusion_v=0.70,
                         recent_dev=- 0.071,
                         recent_dev_scaled=-2.05)
    ]

    rm = RiskManager(entry_z=2, exit_z=0.5)
    rm.run_risk_manager(cointegrated_pairs=test_input, current_window=win)
