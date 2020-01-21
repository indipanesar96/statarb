from typing import Tuple
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
        file_name = f"{self.window_start.year}_sp500_ticker_data.csv"
        sp_500_loc = f"./resources/SP500/{file_name}"

        etf_loc = f"./resources/ETF_data/2008-2019_ETF_data.csv"

        sp500_window = read_excel(sp_500_loc, squeeze=True, header=0, index_col=0,
                                  name=f"{self.window_start}_{self.window_end}")

        etf_window = read_excel(etf_loc, squeeze=True, header=0, index_col=0,
                                name=f"{self.window_start}_{self.window_end}")
        pass

    def pull_initial(self) -> Tuple[Df]:
        pass

    def get_data_for_coint(self, stock_ticker: str, ETF_ticker: str) -> Df:
        pass

    # pulls price data for relevant stocks

    def get_data_for_clustering(self, n) -> Df:
        pass

    # average data over latest n days for all stocks
    # stocks and data as row - as feature is a column
    def leverage(self):
        pass

    def ROE(self):
        pass

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
