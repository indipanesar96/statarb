import re
from datetime import date
from enum import Enum, unique
from pathlib import Path
from typing import Dict, Optional, Set

import pandas as pd
from pandas import DataFrame


@unique
class DataLocations(Enum):
    SNP = Path(f"../resources/SP500/sp_500_ticker_data_all.csv")
    ETFs = Path(f"../resources/ETF_data/2008-2019_ETF_data.csv")


class DataRepository:
    def __init__(self):
        # Loads data on first get call
        self.all_data: Dict[DataLocations, Optional[DataFrame]] = {DataLocations.SNP: None, DataLocations.ETFs: None}
        self.tickers: Dict[DataLocations, Optional[Set[str]]] = {DataLocations.SNP: None, DataLocations.ETFs: None}
        self.features: Dict[DataLocations, Optional[Set[str]]] = {DataLocations.SNP: None, DataLocations.ETFs: None}

    def get(self,
            datatype: DataLocations,
            window_start: date,
            window_end: date):

        if self.all_data[datatype] is None:
            data_for_all_time = self.__get_from_disk_and_store(datatype)
        else:
            data_for_all_time = self.all_data[datatype]

        date_range_filter_mask = [i.date() for i in iter(pd.date_range(start=window_start, end=window_end))]

        return data_for_all_time[data_for_all_time.index.isin(date_range_filter_mask)]

    '''
    dp = DataRepository()
    DataRepository.get() returns a 3 dimensional dataframe
    
    after retrieving full dataset, you can use pandas.IndexSlice to select tickers and features
    
    pandas documentation: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.IndexSlice.html?highlight=indexslice#pandas.IndexSlice
    
    example:
    
    under class PairTrader:
    
    data = self.repository.all_data[DataLocations.SNP]
    
    # all features for stock ['AMCR', 'EVRG']: 
    data.loc[:, pd.IndexSlice[ ['AMCR','EVRG'] , :] ]
    
    # all ticker's ['EBITDA', 'EARN_FOR_COMMON']
    data.loc[:, pd.IndexSlice[ :, ['EBITDA', 'EARN_FOR_COMMON'] ]]
    
    # ['EBITDA', 'EARN_FOR_COMMON'] of ['AMCR', 'EVRG']
    data.loc[:, pd.IndexSlice[ ['AMCR', 'EVRG'] , ['EBITDA', 'EARN_FOR_COMMON'] ]]
    
    '''




    def __get_from_disk_and_store(self, datatype: DataLocations):
        print(f"In DataRepository, reading CSV from disk for: {datatype.name}")

        # Currently we just load all data into memory - not horrific for now but definitely needs to be changed in
        # future as we'll throw an OutOfMemory eventually. Heap usage ~650mb for ETF and SNP all data CSVs

        d = pd.read_csv(datatype.value,
                        squeeze=True,
                        header=0,
                        index_col=0)

        d.index = pd.to_datetime(d.index, format='%d/%m/%Y')

        match_results = [re.findall(r"(\w+)", col) for col in d.columns]
        tickers = [r[0].upper() for r in match_results]
        features = [r[-1].upper() for r in match_results]

        self.tickers[datatype] = set(tickers)
        self.features[datatype] = set(features)

        tuples = list(zip(tickers, features))
        multi_column = pd.MultiIndex.from_tuples(tuples, names=['ticker', 'feature'])
        d.columns = multi_column
        # d.columns = [' '.join((i, j)) for i, j in zip(tickers, features)]

        self.all_data[datatype] = d

        return d

    # def get_data_for_coint(self, stock_ticker: str, ETF_ticker: str) -> Df:
    #     stock_price_data = self[[stock_ticker + ' Last']]
    #     ETF_price_data = self[[ETF_ticker + ' Last']]
    #     data = pd.merger(type = 'outer', stock_price_data, ETF_price_data)
    #     return data
    #     # pulls price data for relevant tickers
    # def get_data_for_clustering(self, tickers: list, tolerance: float): -> Df:
    #     # scan for nas
    #
    #     return df
    #
    # # pulls price data for relevant stocks
    #
    # # average data over latest n days for all stocks
    # # stocks and data as row - as feature is a column
    # def leverage(self, stock_ticker: str):
    #     self['Leverage'] = self[stock_ticker + ' Total Debt']/ self[stock_ticker+ ' Total Assets']
    #
    # def roe(self, stock_ticker: str):
    #     self['ROE'] = self[stock_ticker + ' Net Income'] / self[stock_ticker + ' Shareholders equity']
    # def fill_nas(self, stock_ticker: str):
    #     earnings_data = []
    #     for x in earnings_data:
    #         self = self[stock_ticker + ' ' + x].fillna(method = 'ffill')
    #     return self
    # def repeat_for_tickers(self, tickers: list):
    #     for x in tickers:
    #         self.fill_nas(self, x)
    #         self.roe(self, x)
    #         self.leverage(self,x)
    #         self.fill_nas(self,x)
    #

    def get_time_series(self, start_date: date, end_date: date, datatype: DataLocations, ticker: str, feature: str):

        # get rid of 'US Equity' string in col headings
        all_data = self.all_data[datatype][f"{ticker} {feature}"]

        raise NotImplementedError

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
