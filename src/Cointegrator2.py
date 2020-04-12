import time
from enum import Enum, unique
from typing import Dict, Tuple

import numpy as np
from numpy import array
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.api import adfuller

from src.DataRepository import DataRepository
from src.DataRepository import Universes
from src.Window import Window
from src.util.Features import SnpFeatures
from src.util.Tickers import Tickers


@unique
class AdfPrecisions(Enum):
    ONE_PCT = '1%'
    FIVE_PCT = '5%'
    TEN_PCT = '10%'


class Cointegrator2:

    def __init__(self,
                 repository: DataRepository,
                 adf_confidence_level: AdfPrecisions,
                 max_mean_rev_time: int,
                 entry_z: float,
                 exit_z: float,
                 current_window: Window,
                 previous_window: Window):
        self.repository: DataRepository = repository
        self.adf_confidence_level: AdfPrecisions = adf_confidence_level
        self.max_mean_rev_time: int = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z
        self.current_window: current_window = current_window
        self.previous_window: Window = previous_window

        self.invested = None

    def sig_gen(self, clustering_results: Dict[int, Tuple[Tuple[Tickers]]]):
        # all poss combinations of pairs
        # run cointegration_analysis

        signal = []
        prev_time = time.time()
        n_tested = 0
        n_cointegrated = 0
        for cluster in clustering_results.values():
            for pair in cluster:

                if n_tested % 100 == 0:
                    print(
                        f'Currently checking cointegration for {[i.name for i in pair]}. Checked {n_tested}. Number cointegrated {n_cointegrated}. Time elapsed: {(time.time() - prev_time):.4f}')

                t1 = self.current_window.get_data(universe=Universes.SNP,
                                                  tickers=[pair[0]],
                                                  features=[SnpFeatures.LAST_PRICE])
                t2 = self.current_window.get_data(universe=Universes.SNP,
                                                  tickers=[pair[1]],
                                                  features=[SnpFeatures.LAST_PRICE])

                residuals, beta = self.__lin_reg(t1, t2)

                adf_test_statistic, adf_critical_values = self.__adf(residuals)
                hl_test = self.__hl(residuals)
                he_test = self.__hurst_exponent_test(residuals)
                most_recent_deviation = self.__return_current_deviation(residuals)

                is_cointegrated = self.__acceptance_rule(adf_test_statistic,
                                                         adf_critical_values,
                                                         self.adf_confidence_level,
                                                         hl_test,
                                                         self.max_mean_rev_time,
                                                         he_test)

                if is_cointegrated:
                    n_cointegrated += 1
                signal.append(is_cointegrated)
                n_tested += 1

        x = 10

        pass

    def __classify_coint_results(self):

        pass

    def __return_current_deviation(self, residuals: array) -> float:
        scaler = StandardScaler()
        scaler.fit(residuals)
        residuals_scaled = scaler.transform(residuals)
        latest_residual_scaled = float(residuals_scaled[-1])
        return latest_residual_scaled

    def __lin_reg(self, x: DataFrame, y: DataFrame) -> Tuple[array, float]:

        log_x = x.applymap(lambda k: np.log(k))
        log_y = y.applymap(lambda k: np.log(k))

        results = LinearRegression().fit(log_x, log_y)
        residuals = log_y - results.predict(log_x)  # e = y - y^
        beta = float(results.coef_[0])

        return np.array(residuals), beta

    def __adf(self, residuals: array):
        '''
        critical values are in the following dictionary form:
            {'1%': -3.4304385694773387,
             '5%': -2.8615791461685034,
             '10%': -2.566790836162312}
        '''

        adf_results = adfuller(residuals)
        adf_test_statistic: float = adf_results[0]
        adf_critical_values: Dict[str, float] = adf_results[4]

        return adf_test_statistic, adf_critical_values

    def __hurst_exponent_test(self, residuals) -> float:

        # lag vector
        tau_vector = []

        # var[ (1 - L^n)y  ]
        variance_delta_vector = []

        max_lags = int(self.current_window.window_length.days * 0.5)

        for lag in range(2, max_lags):
            #   (1 - L^n)y
            delta_res = residuals[lag:] - residuals[:-lag]

            tau_vector.append(lag)

            variance_delta_vector.append(
                np.var(delta_res)
            )

        # avoid 0 values for variance_delta_vector
        variance_delta_vector = [value if value != 0 else 1e-10 for value in variance_delta_vector]

        residuals, beta = self.__lin_reg(DataFrame(tau_vector), DataFrame(variance_delta_vector))

        # https://quant.stackexchange.com/questions/35513/explanation-of-standard-method-generalized-hurst-exponent

        return beta / 2

    def __hl(self, residuals: array) -> float:

        # independent variable
        lagged_residuals = residuals[:-1]

        # dependent variable
        delta_residuals = (residuals[1:] - lagged_residuals)
        results = LinearRegression().fit(lagged_residuals, delta_residuals)
        pi = float(results.coef_[0])

        # calculate average time of mean reversion from average speed of mean reversion as per formula
        hl_ave_mean_rev_time = np.log(2) / (-pi)
        return hl_ave_mean_rev_time

    def __acceptance_rule(self,
                          adf_test_statistic: float,
                          adf_critical_values: Dict[str, float],
                          adf_confidence_level: AdfPrecisions,
                          hl_test: float,
                          max_mean_rev_time: int,
                          he_test: float):

        adf = adf_test_statistic < adf_critical_values[adf_confidence_level]
        hl = hl_test < max_mean_rev_time
        he = he_test < 0.5

        return all([adf, hl, he])
