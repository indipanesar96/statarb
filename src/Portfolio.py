import logging
from datetime import date, timedelta

import numpy as np
import pandas as pd
from pandas import DataFrame, to_datetime

from src.DataRepository import Universes, DataRepository
from src.RiskManager import RiskManager
from src.Window import Window
from src.util.Features import Features, PositionType
from src.util.Tickers import SnpTickers, Tickers


class Position:
    def __init__(self,
                 ticker1,
                 ticker2,
                 weight1,
                 weight2,
                 investment_type: PositionType,
                 init_value=100,
                 commission=0):
        self.asset1: Tickers = ticker1
        self.asset2: Tickers = ticker2
        self.weight1: float = weight1
        self.weight2: float = weight2
        self.quantity1: float = 0
        self.quantity2: float = 0
        self.position_type: PositionType = investment_type
        self.log_return: float = 0
        self.commission: float = commission
        self.init_value: float = init_value
        self.current_value: float = init_value
        self.pnl: float = -commission
        self.pos_hist = list()
        self.closed = False

    def set_position_value(self, value, q1, q2):
        self.init_value = value
        self.current_value = value
        self.quantity1 = q1
        self.quantity2 = q2

    def update_weight(self, asset1_val, asset2_val):
        self.weight1 = asset1_val / (asset1_val + asset2_val)
        self.weight2 = asset2_val / (asset1_val + asset2_val)

    def update_position_pnl(self, value, window):
        if not self.closed:
            self.pnl += value - self.current_value
            self.log_return = np.log(value) - np.log(self.current_value)
            self.current_value = value
        self.pos_hist.append([window.window_end, self.current_value, self.pnl, self.log_return])

    def rebalance_pos(self, new_weights, rebalance_value):
        self.weight1 = new_weights[0]
        self.weight2 = new_weights[1]
        self.pnl -= self.commission
        self.current_value += rebalance_value

    def close_trade(self, value, window):
        self.pnl += value - self.current_value - self.commission
        self.current_value = value
        self.closed = True
        self.pos_hist.append([window.window_end, self.current_value, self.pnl])

    def get_pos_hist(self):
        # returns a time series of position value and pnl
        df = DataFrame(self.pos_hist, columns=['date', 'pos_value', 'pnl', 'return'])
        df['date'] = to_datetime(df['date'])
        df = df.set_index('date')
        return df.round(2)


class Portfolio:

    def __init__(self, cash: float, window: Window):
        # port_value: value of all the positions we have currently
        # cur_positions: list of all current positions
        # hist_positions: list of all positions (both historical and current)
        # realised_pnl: realised pnl after closing position (commission included)

        self.init_cash = cash
        self.cur_cash = cash
        self.cur_positions = list()
        self.hist_positions = list()
        self.total_capital = [cash]
        self.active_port_value = float(0)
        self.realised_pnl = float(0)
        self.log_return = float(0)
        self.cum_return = float(0)
        self.t_cost = float(0.0005)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.current_window: Window = window
        self.port_hist = list()
        self.rebalance_threshold = float(1)
        self.loading = float(0.1)
        self.number_active_pairs = 0


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

        pair_dedicated_cash = self.init_cash * self.loading / max(abs(position.weight1), abs(position.weight2))
        quantity1 = round(pair_dedicated_cash * position.weight1 / cur_price.iloc[-1, 0])
        quantity2 = round(pair_dedicated_cash * position.weight2 / cur_price.iloc[-1, 1])
        commission = self.t_cost * (abs(position.quantity1) + abs(position.quantity2))
        asset1_value = cur_price.iloc[-1, 0] * quantity1
        asset2_value = cur_price.iloc[-1, 1] * quantity2
        pair_dedicated_cash = asset1_value + asset2_value
        position.set_position_value(pair_dedicated_cash, quantity1, quantity2)

        if pair_dedicated_cash > self.cur_cash and self.number_active_pairs<=10:
            self.logger.info('No sufficient cash to open position')
        else:
            self.logger.info("%s, %s are cointegrated and zscore is in trading range. Opening position....",
                             position.asset1, position.asset2)
            self.number_active_pairs+=1
            self.cur_positions.append(position)
            self.hist_positions.append(position)

            self.cur_cash -= pair_dedicated_cash + commission
            self.active_port_value += pair_dedicated_cash
            self.logger.info('Asset 1: %s @$%s Quantity: %s Value: %s', position.asset1,
                             round(cur_price.iloc[-1, 0],2), round(quantity1,2), round(asset1_value,2))
            self.logger.info('Asset 2: %s @$%s Quantity: %s Value: %s', position.asset2,
                             round(cur_price.iloc[-1, 1],2), round(quantity2,2), round(asset2_value,2))
            self.logger.info('Cash balance: $%s', self.cur_cash)

    # def close_position(self, ticker1, ticker2):
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

            commission = self.t_cost * (abs(position.quantity1) + abs(position.quantity2))
            asset_value = cur_price.iloc[-1, 0] * position.quantity1 + cur_price.iloc[-1, 1] * position.quantity2

            position.close_trade(asset_value, self.current_window)
            self.cur_cash += asset_value - commission
            self.active_port_value -= asset_value
            self.realised_pnl += position.pnl
            self.logger.info('Asset 1: %s @$%s Quantity: %s', position.asset1,
                             round(cur_price.iloc[-1, 0],2), round(position.quantity1,2))
            self.logger.info('Asset 2: %s @$%s Quantity: %s', position.asset2,
                             round(cur_price.iloc[-1, 1],2), round(position.quantity2,2))
            self.logger.info('Realised PnL for position: %s' % round(position.pnl,2))

    def rebalance(self, position: Position, new_weights):
        cur_price = self.current_window.get_data(universe=Universes.SNP, tickers=[position.asset1, position.asset2],
                                                 features=[Features.CLOSE])

        if position in self.cur_positions:
            position.update_weight(cur_price.iloc[-1, 0]*position.quantity1, cur_price.iloc[-1, 1]*position.quantity2)
            weight1_chg = new_weights[0] - position.weight1
            weight2_chg = new_weights[1] - position.weight2
            if abs(weight1_chg) + abs(weight2_chg) >= self.rebalance_threshold:
                quantity1_chg = (position.current_value * new_weights[0] / cur_price.iloc[-1, 0]) - position.quantity1
                quantity2_chg = (position.current_value * new_weights[1] / cur_price.iloc[-1, 1]) - position.quantity2
                commission = self.t_cost * (abs(quantity1_chg) + abs(quantity2_chg))
                asset_value = cur_price.iloc[-1, 0] * quantity1_chg + cur_price.iloc[-1, 1] * quantity2_chg
                self.logger.info('Rebalancing position...')
                position.rebalance_pos(new_weights, asset_value)
                self.cur_cash -= asset_value + commission
                self.active_port_value += asset_value
                self.logger.info('Asset 1: %s @$%s Quantity: %s', position.asset1, cur_price.iloc[-1, 0], quantity1_chg)
                self.logger.info('Asset 2: %s @$%s Quantity: %s', position.asset2, cur_price.iloc[-1, 1], quantity2_chg)
                self.logger.info('Cash balance: $%s', self.cur_cash)

    def update_portfolio(self):
        cur_port_val = 0

        for pair in self.cur_positions:
            cur_price = self.current_window.get_data(universe=Universes.SNP, tickers=[pair.asset1, pair.asset2],
                                                     features=[Features.CLOSE])
            asset_value = cur_price.iloc[-1, 0] * pair.quantity1 + cur_price.iloc[-1, 1] * pair.quantity2
            pair.update_position_pnl(asset_value, self.current_window)
            cur_port_val += asset_value

        # Compute portfolio stats
        self.active_port_value = cur_port_val
        self.total_capital.append(self.cur_cash+self.active_port_value)
        self.log_return = np.log(self.total_capital[-1]) - np.log(self.total_capital[-2])
        self.cum_return = np.log(self.total_capital[-1]) - np.log(self.total_capital[0])
        self.port_hist.append([self.current_window.window_end, self.cur_cash, self.active_port_value,
                               self.cur_cash + self.active_port_value, self.realised_pnl, self.log_return*100,
                               self.cum_return*100])

    def execute_trades(self, decisions):
        for decision in decisions:
            if decision.old_action is not decision.new_action:
                if decision.old_action is PositionType.NOT_INVESTED:
                    self.open_position(decision.position)
                elif decision.new_action is PositionType.NOT_INVESTED:
                    self.close_position(decision.position)


    def evolve(self):
        self.current_window = self.current_window.evolve()

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
        df = DataFrame(self.port_hist, columns=['date', 'cash', 'port_value', 'total_capital', 'realised_pnl', 'return', 'cum_return'])
        df['date'] = to_datetime(df['date'])
        df = df.set_index('date')
        return df.round(2)


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

    port.evolve()
    port.close_position(p1)
    port.update_portfolio()

    print(port.get_port_hist())

    positions = port.get_hist_positions()
    print(positions[0].asset1, positions[0].asset2)
    print(positions[0].get_pos_hist())
