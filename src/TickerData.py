import pandas as pd
from datetime import date
from src.Scraper import Scraper

class TickerData(object):

    def __init__(self, ticker: str, start_date: date, end_date: date) -> object:
        """
        :rtype: object
        """
        d = Scraper.scrape(ticker, start_date, end_date)
        self.returns: pd.Series = d[0]
        self.cumulative_returns: pd.Series = d[1]
