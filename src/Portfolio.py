from datetime import datetime, date, timedelta
from logging import Logger

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas import DataFrame, to_datetime

from src.DataRepository import Universes, DataRepository
from src.Performance import get_performance_stats
from src.Position import Position
from src.Window import Window
from src.util.Features import Features, PositionType
from src.util.Tickers import SnpTickers


class Portfolio:

    def __init__(self, cash: float, window: Window,
                 logger: Logger, max_active_pairs: float = 10):
        # port_value: value of all the positions we have currently
        # cur_positions: list of all current positions
        # hist_positions: list of all positions (both historical and current)
        # realised_pnl: realised pnl after closing position (commission included)

        self.init_cash = cash
        self.cur_cash = cash
        self.logger = logger
        self.cur_positions = list()
        self.hist_positions = list()
        self.total_capital = [cash]
        self.active_port_value = float(0)
        self.realised_pnl = float(0)
        self.log_return = float(0)
        self.cum_return = float(0)
        self.t_cost = float(0.0005)
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M")

        self.current_window: Window = window
        self.port_hist = list()
        self.rebalance_threshold = float(1)
        self.loading = float(0.1)
        self.number_active_pairs = 0
        self.max_active_pairs = max_active_pairs

        self.port_hist.append(
            [self.current_window.window_end + pd.DateOffset(-1), self.cur_cash, self.active_port_value,
             self.cur_cash + self.active_port_value, self.realised_pnl, self.log_return * 100,
             self.cum_return * 100, self.number_active_pairs])

    def reset_values(self):
        self.cur_cash = self.init_cash
        self.cur_positions = list()
        self.active_port_value = float(0)
        self.realised_pnl = float(0)

    def open_position(self,
                      position: Position):

        cur_price = self.current_window.get_data(universe=Universes.SNP,
                                                 tickers=[position.asset1, position.asset2],
                                                 features=[Features.CLOSE])
        # notional reference amount for each pair. Actual positions are scaled accordingly with respect to
        # maximum weight as per below formula
        pair_dedicated_cash = self.init_cash * self.loading / max(abs(position.weight1), abs(position.weight2))
        position.quantity1 = int(pair_dedicated_cash * position.weight1 / cur_price.iloc[-1, 0])
        position.quantity2 = int(pair_dedicated_cash * position.weight2 / cur_price.iloc[-1, 1])
        asset1_value = cur_price.iloc[-1, 0] * position.quantity1
        asset2_value = cur_price.iloc[-1, 1] * position.quantity2
        commission = self.generate_commission(asset1_value, asset2_value)
        pair_dedicated_cash = asset1_value + asset2_value
        position.set_position_value(pair_dedicated_cash)

        if pair_dedicated_cash > self.cur_cash:
            self.logger.info('No sufficient cash to open position')
        elif self.number_active_pairs >= self.max_active_pairs:
            pass
            # self.logger.info('Active pairs > Maximum pairs')
        else:
            self.logger.info("%s, %s are cointegrated and zscore is in trading range. Opening position....",
                             position.asset1, position.asset2)
            self.number_active_pairs += 1
            self.cur_positions.append(position)
            self.hist_positions.append(position)

            self.cur_cash -= pair_dedicated_cash + commission
            self.active_port_value += pair_dedicated_cash
            self.logger.info('Asset 1: %s @$%s Quantity: %s Value: %s', position.asset1,
                             round(cur_price.iloc[-1, 0], 2), round(position.quantity1, 2), round(asset1_value, 2))
            self.logger.info('Asset 2: %s @$%s Quantity: %s Value: %s', position.asset2,
                             round(cur_price.iloc[-1, 1], 2), round(position.quantity2, 2), round(asset2_value, 2))
            self.logger.info('Cash balance: $%s', self.cur_cash)

    def close_position(self, position: Position):
        cur_price = self.current_window.get_data(universe=Universes.SNP,
                                                 tickers=[position.asset1, position.asset2],
                                                 features=[Features.CLOSE])
        if not (position in self.cur_positions):
            print("dont have this position open")
        else:
            self.logger.info("Closing/emergency threshold is passed for active pair %s, %s. Closing position...",
                             position.asset1, position.asset2)
            self.number_active_pairs -= 1
            self.cur_positions.remove(position)

            asset1_value = cur_price.iloc[-1, 0] * position.quantity1
            asset2_value = cur_price.iloc[-1, 1] * position.quantity2
            commission = self.generate_commission(asset1_value, asset2_value)
            pair_residual_cash = asset1_value + asset2_value

            position.close_trade(pair_residual_cash, self.current_window)
            self.cur_cash += pair_residual_cash - commission
            self.active_port_value -= pair_residual_cash
            self.realised_pnl += position.pnl
            self.logger.info('Asset 1: %s @$%s Quantity: %s', position.asset1,
                             round(cur_price.iloc[-1, 0], 2), int(position.quantity1))
            self.logger.info('Asset 2: %s @$%s Quantity: %s', position.asset2,
                             round(cur_price.iloc[-1, 1], 2), int(position.quantity2))
            self.logger.info('Realised PnL for position: %s' % round(position.pnl, 2))

    def generate_commission(self, asset1_value, asset2_value):
        # transaction costs as % of notional amount
        return self.t_cost * (abs(asset1_value) + abs(asset2_value))

    def update_portfolio(self, today: date):
        cur_port_val = 0

        for pair in self.cur_positions:
            todays_prices = self.current_window.get_data(universe=Universes.SNP,
                                                         tickers=[pair.asset1, pair.asset2],
                                                         features=[Features.CLOSE]).loc[today]

            asset_value = todays_prices[0] * pair.quantity1 + todays_prices[1] * pair.quantity2
            pair.update_position_pnl(asset_value, self.current_window)
            cur_port_val += asset_value

        # Compute portfolio stats
        self.active_port_value = cur_port_val
        self.total_capital.append(self.cur_cash + self.active_port_value)
        self.log_return = np.log(self.total_capital[-1]) - np.log(self.total_capital[-2])
        self.cum_return = np.log(self.total_capital[-1]) - np.log(self.total_capital[0])
        self.port_hist.append([self.current_window.window_end, self.cur_cash, self.active_port_value,
                               self.cur_cash + self.active_port_value, self.realised_pnl, self.log_return * 100,
                               self.cum_return * 100, self.number_active_pairs])
        print(f"Total Capital: {self.total_capital[-1]:.4f}\tCum Return: {self.cum_return:4f}")

    def execute_trades(self, decisions):
        self.logger.info(f"Executing trades for {self.current_window.window_end.strftime('%Y-%m-%d')}")
        for decision in decisions:
            if decision.old_action is not decision.new_action:
                if decision.old_action is PositionType.NOT_INVESTED:
                    self.open_position(decision.position)
                elif decision.new_action is PositionType.NOT_INVESTED:
                    self.close_position(decision.position)

    def get_current_positions(self):
        return self.cur_positions

    def get_hist_positions(self):
        return self.hist_positions

    def get_cash_balance(self):
        return self.cur_cash

    def get_port_summary(self):
        data = list()
        for pair in self.cur_positions:
            data.append([pair.asset1, pair.quantity1, pair.asset2, pair.quantity2, pair.pnl])

        df = DataFrame(data, columns=['Asset 1', 'Quantity 1', 'Asset 2', 'Quantity 2', 'PnL'])

        print('------------------Portfolio Summary------------------')
        print('Current cash balance: \n %s' % self.cur_cash)
        if len(data) != 0:
            print('Current Positions: ')
            print(df)
        else:
            print('No Current Positions')
        print('Realised PnL: \n %s' % self.realised_pnl)
        print('-----------------------------------------------------')
        return [self.cur_cash, df, self.realised_pnl]

    def get_port_hist(self):
        # returns a time series of cash balance, portfolio value and actual pnl
        pd.set_option('expand_frame_repr', False)
        df = DataFrame(self.port_hist, columns=['date', 'cash', 'port_value', 'total_capital',
                                                'realised_pnl', 'return',
                                                'cum_return', 'active_pairs'])
        df['date'] = to_datetime(df['date'])
        df = df.set_index('date')
        return df.round(2)

    def summary(self):
        prc_hist = self.get_port_hist()['total_capital']
        date_parser = lambda x: pd.datetime.strptime(x, '%d/%m/%Y')

        yearly_to_daily = lambda x: x / 365
        pct_to_num = lambda x: x / 100

        tbill = pd.read_csv("../resources/3m_tbill_daily.csv", index_col='date', date_parser=date_parser)

        tbill = tbill.applymap(yearly_to_daily)
        tbill = tbill.applymap(pct_to_num)

        tbill.index += timedelta(1)
        tbill = tbill.loc[tbill.index.intersection(prc_hist.index)]

        print(get_performance_stats(prc_hist, tbill))
        sns.lineplot(data=prc_hist.reset_index(), x='date', y='total_capital')
        plt.show()
        # return performance stats of pnl history


if __name__ == '__main__':
    current_window = Window(window_start=date(2008, 1, 3), trading_win_len=timedelta(days=90),
                            repository=DataRepository())

    port = Portfolio(10000, current_window)
    p1 = Position(SnpTickers.AAPL, SnpTickers.GOOGL, 1.5, -0.5, PositionType.LONG)
    port.open_position(p1)
    port.update_portfolio()

    # port.evolve()
    # port.rebalance(p1, [1.5, -1.5])
    # port.update_portfolio()

    # fundamental data from 2008 (2nd)
    # only load from disk data required for the next window - speeding -IP
    #   past 20 day lookback vol of returns, -TY&SC
    #   volumes, -TY&SC
    #   60 day lookback cum returns (momentum -like) -TY&SC
    # can change eps factor to play with clustering
    # accurate measure of vol for the portfolio -> SR -SP
    # finish implementation of max dd -SC
    # Logging to a file, combined with SC's csv for df - OY
    #

    current_window.roll_forward_one_day()
    port.close_position(p1)
    port.update_portfolio()

    print(port.get_port_hist())

    positions = port.get_hist_positions()
    print(positions[0].asset1, positions[0].asset2)
    print(positions[0].get_pos_hist())
