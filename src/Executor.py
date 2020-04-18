import time
from enum import Enum, unique
from typing import Dict, Tuple
from datetime import date, timedelta

import numpy as np
from numpy import array
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.api import adfuller
from src.Cointegrator import Cointegrator
from src.Cointegrator2 import Cointegrator2
from src.Cointegrator2 import AdfPrecisions
from src.DataRepository import DataRepository
from src.DataRepository import Universes
from src.Window import Window
from src.util.Features import Features
from src.util.Tickers import Tickers
from src.Clusterer import Clusterer
from src.util.Tickers import SnpTickers



class Executor:

    def __init__(self, repository, entry_z, exit_z, current_window, window_end, cointegrator):
        self.repository: DataRepository = repository
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z
        self.current_window: Window = current_window
        self.window_end: date = window_end
        #self.cointegrator2: Cointegrator2 = cointegrator2
        self.cointegrator: Cointegrator = cointegrator
        self.Holding_list = list()
        self.invested = None
        #self.qty: int = qty





    def trade_signals(self, X, Y):
        t1 = self.current_window.get_data(universe=Universes.SNP, tickers=[X],
                                          features=[Features.CLOSE])
        t2 = self.current_window.get_data(universe=Universes.SNP, tickers=[Y],
                                          features=[Features.CLOSE])
        # beta = self.cointegrator.__lin_reg(t1, t2)[1]
        # residual = self.cointegrator.__lin_reg(t1, t2)[0]
        # zscore = self.cointegrator.__return_current_deviation(residual)
        cointegration_parameters = self.cointegrator.cointegration_analysis(t1, t2)  # (X,Y)
        adf_test_statistic, adf_critical_values, hl_test, \
        hurst_exp, beta, latest_residual_scaled = cointegration_parameters
        zscore = latest_residual_scaled
        print(beta)
        print(zscore)
        print(self.invested)
        # If we are not in the market
        if self.invested is None:
            if zscore < -self.entry_z: # Long Entry # Short stock1, long stock2
                stock1_holding = -beta
                stock2_holding = 1
                self.Holding_list.append([stock1_holding, stock2_holding])
                print('1')
                self.invested = "long"

            elif zscore > self.entry_z: # Short Entry # Long stock1, short stock2
                stock1_holding = beta
                stock2_holding = -1
                self.Holding_list.append([stock1_holding, stock2_holding])
                print('2')
                self.invested = "short"

            else:
                stock1_holding = 0
                stock2_holding = 0
                self.Holding_list.append([stock1_holding, stock2_holding])
                print('3')
                self.invested = None


        # If we are in the market
        elif self.invested is not None:
            if self.invested == "long" and zscore < -self.exit_z: # Holding Postion
                stock1_holding = -self.Holding_list[-1][0]  # or equal to the previous window -beta
                stock2_holding = 1
                self.Holding_list.append([stock1_holding, stock2_holding])
                print('4')
                self.invested = "long"
            elif self.invested == "long" and zscore >= -self.exit_z: # Close Position
                stock1_holding = self.Holding_list[-1][0]
                stock2_holding = -1
                self.Holding_list.append([stock1_holding, stock2_holding])
                print('5')
                self.invested = None
            elif self.invested == "short" and zscore > self.exit_z: # Holding Position
                stock1_holding =  self.Holding_list[-1][0]  # or equal to the previous window beta
                stock2_holding = -1
                self.Holding_list.append([stock1_holding, stock2_holding])
                print('6')
                self.invested = "short"
                print(self.invested)
            elif self.invested == "short" and zscore <= self.exit_z: # Close Position
                stock1_holding = -self.Holding_list[-1][0]
                stock2_holding = 1
                self.Holding_list.append([stock1_holding, stock2_holding])
                print('7')
                self.invested = None
        else:
            # Not conintegrated
            stock1_holding = 0
            stock2_holding = 0
            self.Holding_list.append([stock1_holding, stock2_holding])
            print('8')
            self.invested = None


    #def close_positon(self, position_to_close: Tuple[str, str], current_portfolio: Df) -> Df:
        '''
        use prices from self.t_minus_one_data (to know what to sell at)
        :param position_to_close: the two wickers whose positions need to be wiped
        :param current_portfolio: df of current port cointaining the tickers above
        :return: new dataframe without positions requiring closing
        '''

     #   pass

    #def open_positions(self, reduced_pairs: Tuple[str, str], reversions, current_risk_metrics) -> Df:
        '''
        use prices from self.t_minus_one_data (to know what to buy at)
        :param reduced_pairs:
        :param reversions:
        :return: new dataframe with old, still open positions, and newly opened positions
        '''
     #   pass

if __name__ == '__main__':
    # 2.5523122023495732, -1
    win = Window(window_start=date(2008, 1, 15),
                 trading_win_len=timedelta(days=90),
                 repository=DataRepository())
    coin = Cointegrator(repository=DataRepository(), adf_confidence_level= AdfPrecisions.ONE_PCT,
                          max_mean_rev_time=15, entry_z=1.5, exit_z=0.5, current_window=win, previous_window=win, window_end = win.window_end)
    EXC = Executor(repository=DataRepository(), current_window=win, entry_z=1.5, exit_z=0.5,
                   window_end=win.window_end, cointegrator=coin)
    for i in range(0,100):
        EXC.trade_signals(SnpTickers.CTAS, SnpTickers.NVDA)
        win = win.evolve()
        #win = win.evolve_rolling()
    print(EXC.Holding_list)


