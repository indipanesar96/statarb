import yfinance as yf
from datetime import date
import pandas as pd
from pandas import ExcelWriter
from pathlib import Path


class Scraper:
    @classmethod
    def scrape_or_read(cls, ticker: str, start_date: date, end_date: date):
        '''
        Checks if the ticker data for the dates required are already on disk.
            i) If they are, they are read and serialized into objects
            ii) If they're not, they are scraped from Yahoo Finance
        :return: returns a tuple of returns and Cumulative returns
        '''

        folder_name = "yahoo-finance-data"
        filename = ticker + '_' + str(start_date) + '_' + str(end_date) + ".xlsx"

        parent_dir: Path = Path.cwd().parent
        parent_dir.joinpath(folder_name).mkdir(exist_ok=True)
        full_location: Path = parent_dir.joinpath(folder_name).joinpath(filename)

        try:
            return cls.__read(full_location, ticker)

        except FileNotFoundError as _:
            print(f"{filename} wasn't found in {parent_dir}. \n\t Pulling data from Yahoo Finance for")
            return cls.__scrape(full_location, ticker, start_date, end_date)

    @classmethod
    def __read(cls, full_location: Path, ticker: str):

        returns = pd.read_excel(str(full_location), squeeze=True, header=0, usecols=[0, 1], index_col=0,
                                name=ticker + " Return")
        cum_return = pd.read_excel(str(full_location), squeeze=True, header=0, usecols=[0, 2], index_col=0,
                                   name=ticker + " Cumulative Return")

        return returns, cum_return

    @classmethod
    def __save(cls, returns: pd.Series, cum_return: pd.Series, full_path: Path):

        writer = ExcelWriter(full_path)
        returns.to_excel(writer, index=True, index_label="Date", header=True, startcol=0, encoding='utf-8')
        cum_return.to_excel(writer, index=False, header=True, startcol=2, encoding='utf-8')
        writer.save()

    @classmethod
    def __scrape(cls, full_location: Path, ticker: str, start_date: date, end_date: date):

        close_prices = yf.download(ticker, str(start_date), str(end_date)).Close
        returns: pd.Series = close_prices.pct_change().rename(ticker + " Return")
        cum_return: pd.Series = returns.cumsum().rename(ticker + " Cumulative Return")
        cls.__save(returns, cum_return, full_location)

        return returns, cum_return
