import itertools
from enum import Enum, unique
from fractions import Fraction
from typing import Dict, Tuple, List

import numpy as np
from numpy import array
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.api import adfuller

from src.DataRepository import DataRepository
from src.DataRepository import Universes
from src.Window import Window
from src.util.Features import Features
from src.util.Tickers import Tickers


class CointegratedPair:

    def __init__(self,
                 pair: Tuple[Tickers],
                 mu_x_ann: float,
                 sigma_x_ann: float,
                 reg_output: LinearRegression,
                 scaled_beta: float,
                 hl: float,
                 ou_mean: float,
                 ou_std: float,
                 ou_diffusion_v: float,
                 recent_dev: float,
                 recent_dev_scaled: float,
                 recent_dev_scaled_hist: list,
                 cointegration_rank: float):
        self.pair: Tuple[Tickers] = pair
        self.mu_x_ann: float = mu_x_ann
        self.sigma_x_ann: float = sigma_x_ann
        self.reg_output: LinearRegression = reg_output
        self.scaled_beta: float = scaled_beta
        self.hl: float = hl
        self.ou_mean = ou_mean
        self.ou_std = ou_std
        self.ou_diffusion_v = ou_diffusion_v
        self.recent_dev: float = recent_dev
        self.recent_dev_scaled: float = recent_dev_scaled
        self.recent_dev_scaled_hist: list = recent_dev_scaled_hist
        self.cointegration_rank: float = cointegration_rank


@unique
class AdfPrecisions(Enum):
    ONE_PCT = r'1%'
    FIVE_PCT = r'5%'
    TEN_PCT = r'10%'


class Cointegrator:

    def __init__(self, repository: DataRepository,
                 target_number_of_coint_pairs: int,
                 adf_confidence_level: AdfPrecisions,
                 max_mean_rev_time: int,
                 entry_z: float,
                 exit_z: float,
                 previous_cointegrated_pairs: List[CointegratedPair]):

        self.repository: DataRepository = repository
        self.target_number_of_coint_pairs: int = target_number_of_coint_pairs
        self.adf_confidence_level: AdfPrecisions = adf_confidence_level
        self.max_mean_rev_time: int = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z
        self.previous_cointegrated_pairs: List[CointegratedPair] = previous_cointegrated_pairs

    def generate_pairs(self,
                       clustering_results: Dict[int, Tuple[Tuple[Tickers]]],
                       hurst_exp_threshold: float, current_window: Window):
        # run cointegration_analysis on all poss combinations of pairs within the same cluster

        current_cointegrated_pairs = []
        n_cointegrated = 0
        tickers_per_cluster = [i for i in clustering_results.values()]

        for cluster in tickers_per_cluster:
            for pair in itertools.combinations(list(cluster), 2):

                t1 = current_window.get_data(universe=Universes.SNP,
                                             tickers=[pair[0]],
                                             features=[Features.CLOSE])
                t2 = current_window.get_data(universe=Universes.SNP,
                                             tickers=[pair[1]],
                                             features=[Features.CLOSE])

                try:
                    # sometimes there are no price data, in which case, skip
                    residuals, beta, reg_output = self.__logged_lin_reg(t1, t2)
                except ValueError:
                    continue
                # for some reason residuals is a (60,1) array not (60,) array when i run the code so have changed input to residuals.flatten
                adf_test_statistic, adf_critical_values = self.__adf(residuals.flatten())
                hl_test = self.__hl(residuals)
                he_test = self.__hurst_exponent_test(residuals, current_window)

                is_cointegrated = self.__acceptance_rule(adf_test_statistic, adf_critical_values,
                                                         self.adf_confidence_level, hl_test, self.max_mean_rev_time,
                                                         he_test, hurst_exp_threshold)

                if is_cointegrated:
                    n_cointegrated += 1
                    r_x = self.__log_returner(t1)
                    mu_x_ann = float(250 * np.mean(r_x))
                    sigma_x_ann = float(250 ** 0.5 * np.std(r_x))
                    ou_mean, ou_std, ou_diffusion_v, recent_dev, recent_dev_scaled = self.__ou_params(residuals)
                    scaled_beta = beta / (beta - 1)
                    recent_dev_scaled_hist = [recent_dev_scaled]
                    cointegration_rank = self.__score_coint(adf_test_statistic, self.adf_confidence_level,
                                                            adf_critical_values, he_test, hurst_exp_threshold, 10)
                    current_cointegrated_pairs.append(
                        CointegratedPair(pair, mu_x_ann, sigma_x_ann, reg_output, scaled_beta,
                                         hl_test, ou_mean, ou_std, ou_diffusion_v,
                                         recent_dev, recent_dev_scaled,
                                         recent_dev_scaled_hist, cointegration_rank))

                    if n_cointegrated == self.target_number_of_coint_pairs:
                        current_cointegrated_pairs = sorted(current_cointegrated_pairs,
                                                            key=lambda coint_pair: coint_pair.cointegration_rank,
                                                            reverse=True)
                        self.previous_cointegrated_pairs = current_cointegrated_pairs
                        return current_cointegrated_pairs

        self.previous_cointegrated_pairs = current_cointegrated_pairs
        return current_cointegrated_pairs

    def __logged_lin_reg(self, x: DataFrame, y: DataFrame) -> Tuple[array, float, LinearRegression]:

        log_x = x.applymap(lambda k: np.log(k))
        log_y = y.applymap(lambda k: np.log(k))

        reg_output = LinearRegression(fit_intercept=False).fit(log_x, log_y)
        residuals = log_y - reg_output.predict(log_x)  # e = y - y^
        beta = float(reg_output.coef_[0])

        return np.array(residuals), beta, reg_output

    def __log_returner(self, x: DataFrame) -> array:
        x = np.array(x)
        r_x = np.log(x[1:]) - np.log(x[:-1])
        return r_x

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

    def __hurst_exponent_test(self, residuals, current_window: Window) -> float:

        # lag vector
        tau_vector = []
        # var[ (1 - L^n)y  ]
        variance_delta_vector = []
        max_lags = int(current_window.window_length.days * 0.5)

        for lag in range(2, max_lags):
            #   (1 - L^n)y
            delta_res = residuals[lag:] - residuals[:-lag]
            tau_vector.append(lag)
            variance_delta_vector.append(np.var(delta_res))

        # avoid 0 values for variance_delta_vector
        variance_delta_vector = [value if value != 0 else 1e-10 for value in variance_delta_vector]

        residuals, beta, reg_output = self.__logged_lin_reg(DataFrame(tau_vector), DataFrame(variance_delta_vector))

        # https://quant.stackexchange.com/questions/35513/explanation-of-standard-method-generalized-hurst-exponent

        return float(beta / 2)

    def __hl(self, residuals: array) -> float:

        # independent variable
        lagged_residuals = residuals[:-1]
        # dependent variable
        delta_residuals = (residuals[1:] - lagged_residuals)
        model = LinearRegression().fit(lagged_residuals, delta_residuals)
        pi = float(model.coef_[0])  # pi = -k * dt
        # calculate average time of mean reversion from average speed of mean reversion as per formula
        hl_ave_mean_rev_time = np.log(2) / (-pi)  # measured in days
        return hl_ave_mean_rev_time

    def __ou_params(self, residuals: array) -> Tuple[float, float, float, float, float]:
        # We assume the residuals of a cointegrated pair is an OU process

        # independent variable
        lagged_residuals = residuals[:-1]
        # dependent variable
        residuals = residuals[1:]
        model = LinearRegression().fit(lagged_residuals, residuals)
        errors = residuals - model.predict(lagged_residuals)
        ou_mean = float(np.mean(residuals))
        ou_std = float(np.std(residuals))
        sigma_errors = float(np.std(errors))
        ou_diffusion_v = 250 ** 0.5 * sigma_errors

        recent_dev = float(residuals[-1])
        recent_dev_scaled = (recent_dev - ou_mean) / ou_std

        return ou_mean, ou_std, ou_diffusion_v, recent_dev, recent_dev_scaled

    def __acceptance_rule(self, adf_test_statistic: float, adf_critical_values: Dict[str, float],
                          adf_confidence_level: AdfPrecisions, hl_test: float, max_mean_rev_time: int, he_test: float,
                          hurst_exp_threshold: float):

        adf = adf_test_statistic < adf_critical_values[adf_confidence_level.value]
        hl = hl_test < max_mean_rev_time
        he = he_test < hurst_exp_threshold

        return all([adf, hl, he])

    def __score_coint(self, t_stat: float,
                      confidence_level: AdfPrecisions,
                      crit_values: Dict[str, float],
                      hurst_stat: float,
                      hurst_threshold: float,
                      n_pair):
        # using score function to maximise number of profitable trades
        dist = abs(t_stat - crit_values[confidence_level.value])
        hurst = abs(hurst_stat - hurst_threshold)
        weights = Fraction.from_float(-0.0042 * n_pair ** 2 + 0.1683 * n_pair + 0.1238).limit_denominator(
            max_denominator=1000000)
        delta = weights.numerator * dist + weights.denominator * hurst
        return delta

    def get_previous_cointegrated_pairs(self, current_window):
        # updating most recent z scores etc for pairs that qwe have already found to be cointegrated

        for coint_pair in self.previous_cointegrated_pairs:
            t1_most_recent = current_window.get_data(universe=Universes.SNP,
                                                       tickers=[coint_pair.pair[0]],
                                                       features=[Features.CLOSE]).iloc[-1:, :]
            t2_most_recent = current_window.get_data(universe=Universes.SNP,
                                                       tickers=[coint_pair.pair[1]],
                                                       features=[Features.CLOSE]).iloc[-1:, :]

            t1_latest_log_price = np.log(float(t1_most_recent.values[0][0]))
            t2_latest_log_price = np.log(float(t2_most_recent.values[0][0]))

            coint_pair.recent_dev = t2_latest_log_price - coint_pair.reg_output.predict(
                np.array(t1_latest_log_price).reshape(-1, 1)
            )

            coint_pair.recent_dev_scaled = (coint_pair.recent_dev - coint_pair.ou_mean) / coint_pair.ou_std
            coint_pair.recent_dev_scaled_hist.append(coint_pair.recent_dev_scaled)

        return self.previous_cointegrated_pairs
