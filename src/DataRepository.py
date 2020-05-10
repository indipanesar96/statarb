import math
import re
from datetime import date
from enum import Enum, unique
from pathlib import Path
from typing import Dict, Optional, Set, List

import pandas as pd
from pandas import DataFrame


from src.util.Features import Features
from src.util.Tickers import EtfTickers, SnpTickers, Tickers


@unique
class Universes(Enum):
    ETFs = Path(f"../resources/all_etfs2.csv")
    SNP = Path(f"../resources/all_snp2.csv")


class DataRepository:
    def __init__(self):
        # Loads data on first get call
        self.all_data: Dict[Universes, Optional[DataFrame]] = {Universes.SNP: None, Universes.ETFs: None}
        self.tickers: Dict[Universes, Optional[Set[Tickers]]] = {Universes.SNP: None, Universes.ETFs: None}
        self.features: Dict[Universes, Optional[Set[Features]]] = {Universes.SNP: None, Universes.ETFs: None}
        self.all_dates: List[date] = self.__load_dates(Universes.SNP)

    def get_tickers(self):
        return self.tickers

    def get(self,
            datatype: Universes,
            trading_dates: List[date]):

        if self.all_data[datatype] is None:
            data_for_all_time = self.__get_from_disk_and_store(datatype)
        else:
            data_for_all_time = self.all_data[datatype]

        weekday_data_for_window = data_for_all_time[data_for_all_time.index.isin(trading_dates)]
        live_tickers, live_ticker_weekday_data = self.remove_dead_tickers(datatype, weekday_data_for_window)

        if datatype is Universes.SNP:
            typed_live_tickers = [SnpTickers(i) for i in live_tickers]
        else:
            typed_live_tickers = [EtfTickers(i) for i in live_tickers]

        return typed_live_tickers, live_ticker_weekday_data

    def remove_dead_tickers(self, datatype: Universes, alive_and_dead_ticker_data: DataFrame):
        # Just gets the first column of data (don't care which feature) of the ticker to see if theyre all nan [dead]
        # If they're all nan, we assume the ticker didnt exist then, and so remove from the window
        # If there are some (or no) nans then the ticker is live

        alive_tickers = [i for i in self.tickers[datatype]]
        junk_val = 'XXXXX'
        for idx, ticker in enumerate(self.tickers[datatype]):

            column = alive_and_dead_ticker_data.loc[:, ticker].iloc[:, 0]
            is_nans = [True if math.isnan(i) else False for i in column]

            if any(is_nans):
                # ticker is alive for this window
                alive_tickers[idx] = junk_val

        alive_tickers = [i for i in alive_tickers if i != junk_val]

        return alive_tickers, alive_and_dead_ticker_data.loc[:, pd.IndexSlice[alive_tickers, :]]

    def __get_from_disk_and_store(self, datatype: Universes):
        print(f"In DataRepository. Reading CSV from disk for: {datatype.name}")

        # Currently we just load all data into memory - not horrific for now but definitely needs to be changed in
        # future as we'll throw an OutOfMemory eventually. Heap usage ~650mb for ETF and SNP all data CSVs

        d = pd.read_csv(datatype.value,
                        squeeze=True,
                        header=0,
                        index_col=0,
                        low_memory=False)

        d.index = pd.to_datetime(d.index, format='%d/%m/%Y')

        # code below is only required if calculating intraday volatility from scratch
        # match_results = [re.findall(r"(\w+)", col) for col in d.columns]
        # tickers = [r[0].upper() for r in match_results]
        # d = self.intraday_vol(d, tickers)

        match_results = [re.findall(r"(\w+)", col) for col in d.columns]
        if datatype is Universes.SNP:
            tickers = [SnpTickers(r[0].upper()) for r in match_results]
            features = [Features(r[-1].upper()) for r in match_results]
        else:
            tickers = [EtfTickers(r[0].upper()) for r in match_results]
            features = [Features(r[-1].upper()) for r in match_results]

        self.tickers[datatype] = set(tickers)
        self.features[datatype] = set(features)

        tuples = list(zip(tickers, features))
        multi_column = pd.MultiIndex.from_tuples(tuples, names=['ticker', 'feature'])
        d.columns = multi_column
        self.all_data[datatype] = self.forward_fill(d)

        return d

    @classmethod
    def forward_fill(cls, df: DataFrame):
        return pd.DataFrame(df).fillna(method='ffill')

    def intraday_vol(self, data: DataFrame, tickers: list):
        features = ["Open",
                    "Adj Close",
                    "High",
                    "Low"]
        for ticker in tickers:
            ft = [ticker + " " +f.title() for f in features]
            ticker_data = data[ft]
            data[ticker + " INTRADAY_VOL"] = ticker_data.std(axis=1)
        return data


    def ROE(self, datatype: Universes, ticker):

        if datatype is Universes.SNP:
            NI_data = pd.Dataframe(self.all_data[datatype][f"{ticker} {'EARN_FOR_COMMON'}"])
            Mcap_data = pd.Dataframe(self.all_data[datatype][f"{ticker} {'TOTAL_EQUITY'}"])
            ROE = NI_data / Mcap_data
            return ROE.fillna(method='ffill')
        else:
            print("An ETF can't have an ROE. I am in src.Datarepository.ROE")
            raise KeyError

    def leverage(self, datatype: Universes, ticker):

        if datatype is Universes.SNP:
            TA_data = pd.Dataframe(self.all_data[datatype][f"{ticker} {'TOTAL_ASSETS'}"])
            TE_data = pd.Dataframe(self.all_data[datatype][f"{ticker} {'TOTAL_EQUITY'}"])
            leverage = TA_data / TE_data
            return leverage.fillna(method='ffill')
        else:
            print("An ETF can't have a Leverage Ratio. I am in src.Datarepository.ROE")
            raise KeyError

    def __load_dates(self, datatype: Universes) -> List[date]:
        d = pd.read_csv(datatype.value,
                        squeeze=True,
                        header=0,
                        index_col=0,
                        usecols=[0])

        return [i.date() for i in pd.to_datetime(d.index, format='%d/%m/%Y')]
