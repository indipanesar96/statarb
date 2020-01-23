from typing import Tuple
from pandas import DataFrame as Df


class Executor:

    def __init__(self, t_minus_one_data: Df):
        self.t_minus_one_data = t_minus_one_data

    def close_positon(self, position_to_close: Tuple[str, str], current_portfolio: Df) -> Df:
        '''
        use prices from self.t_minus_one_data (to know what to sell at)
        :param position_to_close: the two wickers whose positions need to be wiped
        :param current_portfolio: df of current port cointaining the tickers above
        :return: new dataframe without positions requiring closing
        '''

        pass

    def open_positions(self, reduced_pairs: Tuple[str, str], reversions, current_risk_metrics) -> Df:
        '''
        use prices from self.t_minus_one_data (to know what to buy at)
        :param reduced_pairs:
        :param reversions:
        :return: new dataframe with old, still open positions, and newly opened positions
        '''
        pass
