import logging
from datetime import date, timedelta

from pandas import DataFrame, to_datetime

from src.DataRepository import Universes, DataRepository
from src.Window import Window
from src.util.Features import Features
from src.util.Tickers import SnpTickers


class Portfolio:

    def __init__(self, cash, window):
        # port_value: value of all the positions we have currently
        # cur_positions: list of all current positions
        # hist_positions: list of all positions (both historical and current)
        # realised_pnl: realised pnl after closing position (commission included)

        self.init_cash = cash
        self.cur_cash = cash
        self.cur_positions = list()
        self.hist_positions = list()
        self.port_value = float(0)
        self.realised_pnl = float(0)
        self.t_cost = float(1)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.current_window = window
        self.port_hist = list()
        self.rebalance_threshold = float(1)

    def reset_values(self):
        self.cur_cash = self.init_cash
        self.cur_positions = list()
        self.port_value = float(0)
        self.realised_pnl = float(0)

    def open_position(self, ticker1, ticker2, quantity1, quantity2):
        cur_price = self.current_window.get_data(universe=Universes.SNP, tickers=[ticker1, ticker2],
                                                 features=[Features.CLOSE])

        commission = self.t_cost * (abs(quantity1) + abs(quantity2))
        asset_value = cur_price.iloc[-1, 0] * quantity1 + cur_price.iloc[-1, 1] * quantity2

        self.logger.info('Opening position...')
        pair = Position(ticker1, ticker2, quantity1, quantity2, asset_value, commission)
        self.cur_positions.append(pair)
        self.hist_positions.append(pair)

        self.cur_cash -= asset_value + commission
        self.port_value += asset_value
        self.logger.info('Asset 1: %s @$%s Quantity: %s', ticker1, cur_price.iloc[-1, 0], quantity1)
        self.logger.info('Asset 2: %s @$%s Quantity: %s', ticker2, cur_price.iloc[-1, 1], quantity2)
        self.logger.info('Cash balance: $%s', self.cur_cash)

    def close_position(self, ticker1, ticker2):
        cur_price = self.current_window.get_data(universe=Universes.SNP, tickers=[ticker1, ticker2],
                                                 features=[Features.CLOSE])
        for pair in self.cur_positions:
            if pair.asset1 == ticker1 and pair.asset2 == ticker2:
                self.logger.info('Closing position...')
                self.cur_positions.remove(pair)

                commission = self.t_cost * (abs(pair.quantity1) + abs(pair.quantity2))
                asset_value = cur_price.iloc[-1, 0] * pair.quantity1 + cur_price.iloc[-1, 1] * pair.quantity2

                pair.close_trade(asset_value, self.current_window)
                self.cur_cash += asset_value - commission
                self.port_value -= asset_value
                self.realised_pnl += pair.pnl
                self.logger.info('Asset 1: %s @$%s Quantity: %s', ticker1, cur_price.iloc[-1, 0], -pair.quantity1)
                self.logger.info('Asset 2: %s @$%s Quantity: %s', ticker2, cur_price.iloc[-1, 1], -pair.quantity2)
                self.logger.info('Realised PnL for position: %s' % pair.pnl)

    def rebalance(self, ticker1, ticker2, quantity1, quantity2):
        cur_price = self.current_window.get_data(universe=Universes.SNP, tickers=[ticker1, ticker2],
                                                 features=[Features.CLOSE])

        for pair in self.cur_positions:
            if pair.asset1 == ticker1 and pair.asset2 == ticker2:
                quantity1 -= pair.quantity1
                quantity2 -= pair.quantity2
                if abs(quantity1) + abs(quantity2) >= self.rebalance_threshold:
                    commission = self.t_cost * (abs(quantity1) + abs(quantity2))
                    asset_value = cur_price.iloc[-1, 0] * quantity1 + cur_price.iloc[-1, 1] * quantity2

                    self.logger.info('Rebalancing position...')
                    pair = Position(ticker1, ticker2, quantity1, quantity2, asset_value, commission)
                    self.cur_cash -= asset_value + commission
                    self.port_value += asset_value
                    self.logger.info('Asset 1: %s @$%s Quantity: %s', ticker1, cur_price.iloc[-1, 0], quantity1)
                    self.logger.info('Asset 2: %s @$%s Quantity: %s', ticker2, cur_price.iloc[-1, 1], quantity2)
                    self.logger.info('Cash balance: $%s', self.cur_cash)

    def update_portfolio(self):
        cur_port_val = 0

        for pair in self.cur_positions:
            cur_price = self.current_window.get_data(universe=Universes.SNP, tickers=[pair.asset1, pair.asset2],
                                                     features=[Features.CLOSE])
            asset_value = cur_price.iloc[-1, 0] * pair.quantity1 + cur_price.iloc[-1, 1] * pair.quantity2
            pair.update_position_pnl(asset_value, self.current_window)
            cur_port_val += asset_value

        self.port_value = cur_port_val
        self.port_hist.append([self.current_window.window_end, self.cur_cash, self.port_value, self.realised_pnl])

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
        df = DataFrame(self.port_hist, columns=['date', 'cash', 'port_value', 'realised_pnl'])
        df['date'] = to_datetime(df['date'])
        df = df.set_index('date')
        return df


class Position:
    def __init__(self, ticker1, ticker2, quantity1, quantity2, init_value, commission):
        self.asset1 = ticker1
        self.asset2 = ticker2
        self.quantity1 = quantity1
        self.quantity2 = quantity2
        self.init_value = init_value
        self.current_value = init_value
        self.commission = commission
        self.pnl = -commission
        self.pos_hist = list()
        self.closed = False

    def update_position_pnl(self, value, window):
        if not self.closed:
            self.pnl += value - self.current_value
            self.current_value = value
        self.pos_hist.append([window.window_end, self.current_value, self.pnl])

    def close_trade(self, value, window):
        self.pnl += value - self.current_value - self.commission
        self.current_value = value
        self.closed = True
        self.pos_hist.append([window.window_end, self.current_value, self.pnl])

    def get_pos_hist(self):
        # returns a time series of position value and pnl
        df = DataFrame(self.pos_hist, columns=['date', 'pos_value', 'pnl'])
        df['date'] = to_datetime(df['date'])
        df = df.set_index('date')
        return df


if __name__ == '__main__':
    current_window = Window(window_start=date(2008, 1, 3), trading_win_len=timedelta(days=90),
                            repository=DataRepository())

    port = Portfolio(10000, current_window)
    port.open_position(SnpTickers.AAPL, SnpTickers.GOOGL, 1, -1)
    port.update_portfolio()

    port.evolve()
    port.close_position(SnpTickers.AAPL, SnpTickers.GOOGL)
    port.update_portfolio()

    port.evolve()
    port.update_portfolio()

    print(port.get_port_hist())

    positions = port.get_hist_positions()
    print(positions[0].asset1, positions[0].asset2)
    print(positions[0].get_pos_hist())
