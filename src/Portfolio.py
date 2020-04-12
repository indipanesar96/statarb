from datetime import date, timedelta
from typing import Optional, List

import pandas as pd

from src.DataRepository import DataRepository, Universes
from src.util.Features import Features
from src.util.Tickers import Tickers






class Portfolio():

    def __init__(self, cash):
        self.cash = cash





    def current_opening_positions(self, ):







    def cash_available(self, ):

'''
create a portfolio class and think about what it will need (ie what goes in _init_),
which functions the portfolio may be asked to do, eg list current open positions,
how much cash we have right now.
It should be a bit like window in the sense that we have a current portfolio
and a history of what our portfolio looked like in the past,
though we can keep all history.
'''