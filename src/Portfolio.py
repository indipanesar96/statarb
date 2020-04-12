from datetime import date, timedelta
from pandas import DataFrame

from src.DataRepository import Universes, DataRepository
from src.Window import Window
from src.util.Features import SnpFeatures
from src.util.Tickers import SnpTickers
import logging


class Portfolio:

    def __init__(self, cash, window):
        self.init_cash = cash
        self.cur_cash = cash
        self.cur_positions = list()
        self.hist_positions = list()
        self.port_value = float(0)
        self.realised_pnl = float(0)
        self.t_cost = float(1)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def reset_values(self):
        self.cur_cash = self.init_cash
        self.cur_positions = list()
        self.port_value = float(0)
        self.realised_pnl = float(0)

    def open_position(self, ticker1, ticker2, quantity1, quantity2, window):
        cur_price = window.get_data(universe=Universes.SNP, tickers=[ticker1, ticker2],
                                    features=[SnpFeatures.LAST_PRICE])

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

    def close_position(self, ticker1, ticker2, window):
        cur_price = window.get_data(universe=Universes.SNP, tickers=[ticker1, ticker2],
                                    features=[SnpFeatures.LAST_PRICE])
        for pair in self.cur_positions:
            if pair.asset1 == ticker1 and pair.asset2 == ticker2:
                self.logger.info('Closing position...')
                self.cur_positions.remove(pair)

                commission = self.t_cost * (abs(pair.quantity1) + abs(pair.quantity2))
                asset_value = cur_price.iloc[-1, 0] * pair.quantity1 + cur_price.iloc[-1, 1] * pair.quantity2

                pair.close_trade(asset_value)
                self.cur_cash += asset_value - commission
                self.port_value -= asset_value
                self.realised_pnl += pair.pnl
                self.logger.info('Asset 1: %s @$%s Quantity: %s', ticker1, cur_price.iloc[-1, 0], -pair.quantity1)
                self.logger.info('Asset 2: %s @$%s Quantity: %s', ticker2, cur_price.iloc[-1, 1], -pair.quantity2)
                self.logger.info('Realised PnL for position: %s' % pair.pnl)

    def update_portfolio(self, window):
        cur_port_val = 0

        for pair in self.cur_positions:
            cur_price = window.get_data(universe=Universes.SNP, tickers=[pair.asset1, pair.asset2],
                                        features=[SnpFeatures.LAST_PRICE])
            asset_value = cur_price.iloc[-1, 0] * pair.quantity1 + cur_price.iloc[-1, 1] * pair.quantity2
            pair.update_position_pnl(asset_value)
            cur_port_val += asset_value

        self.port_value = cur_port_val

    def get_current_positions(self):
        return self.cur_positions

    def get_cash_balance(self):
        return self.cur_cash

    def get_port_summary(self):
        data = list()
        for pair in self.cur_positions:
            mtm = pair.current_value - pair.current_value
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
        self.closed = False

    def update_position_pnl(self, value):
        if not self.closed:
            self.pnl += value - self.current_value
            self.current_value = value

    def close_trade(self, value):
        self.current_value = value
        self.pnl += value - self.current_value - self.commission
        self.closed = True


if __name__ == '__main__':
    current_window = Window(window_start=date(2008, 1, 1), window_length=timedelta(days=90),
                            repository=DataRepository())

    port = Portfolio(10000, current_window)
    port.open_position(SnpTickers.AAPL, SnpTickers.GOOGL, 1, -1, current_window)

    current_window.evolve()
    port.update_portfolio(current_window)
    port.get_port_summary()

    port.close_position(SnpTickers.AAPL, SnpTickers.GOOGL, current_window)
    port.get_port_summary()