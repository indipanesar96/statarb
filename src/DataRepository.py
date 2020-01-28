from typing import Tuple
import pandas as pd
from pandas import DataFrame as Df
from pandas import read_excel
import datetime


class DataRepository:
    '''
    Handles all interfaces with data from file or from bloomberg/yfinance

    pull_latest, pull_initial, get_data_for_coint - all do v similar thing -
    they should all wrap an internal (hidden) function and then mangle the datatype into what
    is specifically required for that method's caller

    this should follow the design pattern of the scraping/reading in the below comment
    '''

    def __init__(self, window_size: datetime.timedelta, data: Tuple[Df] = None):
        self.data = self.retrieve_window() if data is None else data
        self.window_start = datetime.date(2008, 1, 1)
        self.window_end = self.window_start + window_size

    def retrieve_window(self) -> Df:
        sp_500_loc = f"./resources/SP500/sp_500_ticker_data_all.csv"

        etf_loc = f"./resources/ETF_data/2008-2019_ETF_data.csv"

        sp500_window = read_excel(sp_500_loc, squeeze=True, header=0, index_col=0,
                                  name=f"{self.window_start}_{self.window_end}")

        etf_window = read_excel(etf_loc, squeeze=True, header=0, index_col=0,
                                name=f"{self.window_start}_{self.window_end}")
        pass

    def pull_initial(self) -> Tuple[Df]:
        pass

    def get_data_for_coint(self, stock_ticker: str, ETF_ticker: str) -> Df:
        stock_price_data = self[[stock_ticker + ' Last']]
        ETF_price_data = self[[ETF_ticker + ' Last']]
        data = pd.merger(type = 'outer', stock_price_data, ETF_price_data)
        return data
        # pulls price data for relevant tickers
    def get_data_for_clustering(self, tickers: list, tolerance: float): -> Df:
        # scan for nas

        return df

    # pulls price data for relevant stocks

    # average data over latest n days for all stocks
    # stocks and data as row - as feature is a column
    def leverage(self, stock_ticker: str):
        self['Leverage'] = self[stock_ticker + ' Total Debt']/ self[stock_ticker+ ' Total Assets']

    def roe(self, stock_ticker: str):
        self['ROE'] = self[stock_ticker + ' Net Income'] / self[stock_ticker + ' Shareholders equity']
    def fill_nas(self, stock_ticker: str):
        earnings_data = []
        for x in earnings_data:
            self = self[stock_ticker + ' ' + x].fillna(method = 'ffill')
        return self
    def repeat_for_tickers(self, tickers: list):
        for x in tickers:
            self.fill_nas(self, x)
            self.roe(self, x)
            self.leverage(self,x)
            self.fill_nas(self,x)



# @classmethod
# def __read(cls, full_location: Path, ticker: str):
#
#     returns = pd.read_excel(str(full_location), squeeze=True, header=0, usecols=[0, 1], index_col=0,
#                             name=ticker + " Return")
#     cum_return = pd.read_excel(str(full_location), squeeze=True, header=0, usecols=[0, 2], index_col=0,
#                                name=ticker + " Cumulative Return")
#     ave_return = returns.mean()
#     std_of_returns = returns.std()
#
#     return returns, cum_return, ave_return, std_of_returns
#
# @classmethod
# def __save(cls, returns: pd.Series, cum_return: pd.Series, full_path: Path):
#
#     writer = ExcelWriter(full_path)
#     returns.to_excel(writer, index=True, index_label="Date", header=True, startcol=0, encoding='utf-8')
#     cum_return.to_excel(writer, index=False, header=True, startcol=2, encoding='utf-8')
#     writer.save()
#
# @classmethod
# def __scrape(cls, full_location: Path, ticker: str, start_date: date, end_date: date):
#
#     close_prices: pd.Series = yf.download(ticker, str(start_date), str(end_date)).Close
#     returns: pd.Series = close_prices.pct_change().rename(ticker + " Return")
#
#     cum_return: pd.Series = returns.cumsum().rename(ticker + " Cumulative Return")
#
#     ave_return = returns.mean()
#     std_of_returns = returns.std()
#
#     cls.__save(returns, cum_return, full_location)
#
#     return returns, cum_return, ave_return, std_of_returns
