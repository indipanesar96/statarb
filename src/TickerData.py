import pandas as pd
from datetime import date
from Scraper import Scraper
from datetime import date


class TickerData(object):

    def __init__(self, ticker: str, start_date: date, end_date: date) -> object:
        """
        :rtype: object
        """
        d = Scraper.scrape_or_read(ticker, start_date, end_date)
        self.returns: pd.Series = d[0]
        self.cumulative_returns: pd.Series = d[1]
        self.ave_return: float = d[2]
        self.std_of_returns: float = d[3]
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.ticker: str = ticker
