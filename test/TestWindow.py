import tempfile
from datetime import date, timedelta
from pathlib import Path
from unittest import TestCase

import numpy as np
import pandas as pd

from src.DataRepository import DataRepository, Universes
from src.Window import Window
from src.util.Features import Features
from src.util.Tickers import EtfTickers, SnpTickers


class TestWindow(TestCase):
    tmp_dir = Path(tempfile.mkdtemp())

    @classmethod
    def setUpClass(cls) -> None:
        cls.initial = Window(date(2008, 1, 2), timedelta(days=10), DataRepository())

    def test_window_initialised_with_non_trading_day(self):
        # 1st of Jan isn't a trading day; the production code should raise a KeyError
        with self.assertRaises(KeyError):
            Window(date(2008, 1, 1), timedelta(days=10), DataRepository())

    def test_window_evolve(self):
        intial_expected_trading_days = [
            date(year=2008, month=1, day=2),
            date(year=2008, month=1, day=3),
            date(year=2008, month=1, day=4),
            date(year=2008, month=1, day=7),
            date(year=2008, month=1, day=8),
            date(year=2008, month=1, day=9),
            date(year=2008, month=1, day=10),
            date(year=2008, month=1, day=11),
            date(year=2008, month=1, day=14),
            date(year=2008, month=1, day=15)
        ]

        self.assertEqual(self.initial.window_end, date(2008, 1, 15))
        self.assertEqual(self.initial.window_length.days, 10)
        self.assertEqual(self.initial.lookback_win_dates, intial_expected_trading_days)

        evolved_window = self.initial.roll_forward_one_day()
        intial_expected_trading_days.append(date(2008, 1, 16))

        self.assertEqual(evolved_window.window_end, date(2008, 1, 16))
        self.assertEqual(evolved_window.window_length.days, 11)
        self.assertEqual(evolved_window.window_trading_days, intial_expected_trading_days)

    def test_window_initialise(self):
        # return all features and tickers

        expected_etf_data = pd.read_csv("test_resources/test_window_initialise_etf.csv", sep=",", index_col=0,
                                        header=[0, 1])

        expected_snp_data = pd.read_csv("test_resources/test_window_initialise_snp.csv", sep=",", index_col=0,
                                        header=[0, 1])

        expected_etf_data.index = pd.to_datetime(expected_etf_data.index, format='%Y/%m/%d')
        expected_snp_data.index = pd.to_datetime(expected_etf_data.index, format='%Y/%m/%d')

        self.check_arrays_are_equal(self.initial.etf_data.values, expected_etf_data.values)
        self.check_arrays_are_equal(self.initial.snp_data.values, expected_snp_data.values)

    def test_window_get_data_vanilla(self):
        # return all features and tickers

        expected_snp_data = pd.read_csv("test_resources/test_window_initialise_snp.csv", sep=",", index_col=0,
                                        header=[0, 1])
        expected_etf_data = pd.read_csv("test_resources/test_window_initialise_etf.csv", sep=",", index_col=0,
                                        header=[0, 1])

        snp_data = self.initial.get_data(Universes.SNP)
        etf_data = self.initial.get_data(Universes.ETFs)

        self.check_arrays_are_equal(snp_data.values, expected_snp_data.values)
        self.check_arrays_are_equal(etf_data.values, expected_etf_data.values)

    def test_window_get_data_feature_subset(self):
        # return all tickers but a subset of the features

        features = [Features.VOLUME, Features.CLOSE]

        snp_data = self.initial.get_data(Universes.SNP, features=features)
        etf_data = self.initial.get_data(Universes.ETFs, features=features)

        self.assertTrue(set(i[1] for i in snp_data.columns) == set(features))
        self.assertTrue(set(i[1] for i in etf_data.columns) == set(features))

        expected_snp_data = pd.read_csv("test_resources/test_window_get_data_snp_feature_subset.csv", sep=",",
                                        index_col=0,
                                        header=[0, 1])
        expected_etf_data = pd.read_csv("test_resources/test_window_get_data_etf_feature_subset.csv", sep=",",
                                        index_col=0,
                                        header=[0, 1])

        self.check_arrays_are_equal(snp_data.values, expected_snp_data.values)
        self.check_arrays_are_equal(etf_data.values, expected_etf_data.values)

    def test_window_get_data_ticker_subset(self):
        # return all features but a subset of the tickers

        snp_tickers = [SnpTickers.AAPL, SnpTickers.MSFT]
        etf_tickers = [EtfTickers.BBH, EtfTickers.VOX]

        snp_data = self.initial.get_data(Universes.SNP, tickers=snp_tickers)
        etf_data = self.initial.get_data(Universes.ETFs, tickers=etf_tickers)

        self.assertTrue(set(i[0] for i in snp_data.columns) == set(snp_tickers))
        self.assertTrue(set(i[0] for i in etf_data.columns) == set(etf_tickers))

        expected_snp_data = pd.read_csv("test_resources/test_window_get_data_snp_ticker_subset.csv", sep=",",
                                        index_col=0,
                                        header=[0, 1])
        expected_etf_data = pd.read_csv("test_resources/test_window_get_data_etf_ticker_subset.csv", sep=",",
                                        index_col=0,
                                        header=[0, 1])

        self.check_arrays_are_equal(snp_data.values, expected_snp_data.values)
        self.check_arrays_are_equal(etf_data.values, expected_etf_data.values)

    def test_window_get_data_ticker_and_feature_subset(self):
        # return all tickers but a subset of the features

        snp_tickers = [SnpTickers.AAPL, SnpTickers.MSFT]
        etf_tickers = [EtfTickers.BBH, EtfTickers.VOX]

        features = [Features.VOLUME, Features.CLOSE]

        snp_data = self.initial.get_data(Universes.SNP, tickers=snp_tickers, features=features)
        etf_data = self.initial.get_data(Universes.ETFs, tickers=etf_tickers, features=features)

        self.assertTrue(set(i[0] for i in snp_data.columns) == set(snp_tickers))
        self.assertTrue(set(i[0] for i in etf_data.columns) == set(etf_tickers))

        self.assertTrue(set(i[1] for i in snp_data.columns) == set(features))
        self.assertTrue(set(i[1] for i in etf_data.columns) == set(features))

        expected_snp_data = pd.read_csv("test_resources/test_window_get_data_snp_ticker_feature_subset.csv", sep=",",
                                        index_col=0,
                                        header=[0, 1])
        expected_etf_data = pd.read_csv("test_resources/test_window_get_data_etf_ticker_feature_subset.csv", sep=",",
                                        index_col=0,
                                        header=[0, 1])

        self.check_arrays_are_equal(snp_data.values, expected_snp_data.values)
        self.check_arrays_are_equal(etf_data.values, expected_etf_data.values)

    def check_arrays_are_equal(self, one, two):
        for i, j in zip(one.astype(np.long).flat,
                        two.astype(np.long).flat):
            self.assertEqual(i, j)
