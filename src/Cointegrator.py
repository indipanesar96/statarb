import time
from enum import Enum, unique
from typing import Dict, Tuple, List
import numpy as np
from numpy import array
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.api import adfuller
from collections import OrderedDict
from operator import itemgetter

from src.DataRepository import DataRepository
from src.DataRepository import Universes
from src.Window import Window
from src.util.Features import Features
from src.util.Tickers import Tickers, SnpTickers


class CointegratedPair:

    def __init__(self,
                 pair: Tuple[Tickers],
                 mu_x_ann: float,
                 sigma_x_ann: float,
                 scaled_beta: float,
                 hl: float,
                 ou_mean: float,
                 ou_std: float,
                 ou_diffusion_v: float,
                 recent_dev: float,
                 recent_dev_scaled: float):

        self.pair: Tuple[Tickers] = pair
        self.mu_x_ann: float = mu_x_ann
        self.sigma_x_ann: float = sigma_x_ann
        self.scaled_beta: float = scaled_beta
        self.hl: float = hl
        self.ou_mean = ou_mean
        self.ou_std = ou_std
        self.ou_diffusion_v = ou_diffusion_v
        self.recent_dev: float = recent_dev
        self.recent_dev_scaled: float = recent_dev_scaled


@unique
class AdfPrecisions(Enum):
    ONE_PCT = r'1%'
    FIVE_PCT = r'5%'
    TEN_PCT = r'10%'


class Cointegrator:

    def __init__(self,
                 repository: DataRepository,
                 adf_confidence_level: AdfPrecisions,
                 max_mean_rev_time: int,
                 entry_z: float,
                 exit_z: float,
                 current_window: Window,
                 previous_window: Window,
                 previous_cointegrated_pairs: List[CointegratedPair]
                 ):

        self.repository: DataRepository = repository
        self.adf_confidence_level: AdfPrecisions = adf_confidence_level
        self.max_mean_rev_time: int = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z: float = exit_z
        self.current_window: current_window = current_window
        self.previous_window: Window = previous_window
        self.previous_cointegrated_pairs: List[CointegratedPair] = previous_cointegrated_pairs


    def generate_pairs(self,
                       clustering_results: Dict[int, Tuple[Tuple[Tickers]]],
                       hurst_exp_threshold: float):
        # run cointegration_analysis on all poss combinations of pairs

        current_cointegrated_pairs = []
        scored_pairs = {}

        list_of_lists = [i for i in clustering_results.values()]
        flattened = [pair for x in list_of_lists for pair in x]

        sorted_cluster_results = sorted(flattened, key=lambda x: x[0].value)

        for pair in sorted_cluster_results:
            t1 = self.current_window.get_data(universe=Universes.SNP,
                                              tickers=[pair[0]],
                                              features=[Features.CLOSE])
            t2 = self.current_window.get_data(universe=Universes.SNP,
                                              tickers=[pair[1]],
                                              features=[Features.CLOSE])

            try:
                # sometimes there are no price data
                residuals, beta = self.__logged_lin_reg(t1, t2)
            except:
                continue
            #for some reason residuals is a (60,1) array not (60,) array when i run the code so have changed input to residuals.flatten
            adf_test_statistic, adf_critical_values = self.__adf(residuals.flatten())
            hl_test = self.__hl(residuals)
            he_test = self.__hurst_exponent_test(residuals)

            is_cointegrated = self.__acceptance_rule(adf_test_statistic, adf_critical_values,
                                                     self.adf_confidence_level, hl_test, self.max_mean_rev_time,
                                                     he_test, hurst_exp_threshold)

            if is_cointegrated:
                r_x = self.__log_returner(t1)
                mu_x_ann = float(250 * np.mean(r_x))
                sigma_x_ann = float(250 ** 0.5 * np.std(r_x))
                ou_mean, ou_std, ou_diffusion_v, recent_dev, recent_dev_scaled = self.__ou_params(residuals)

                scaled_beta = beta / (beta - 1)
                current_cointegrated_pairs.append(CointegratedPair(pair, mu_x_ann, sigma_x_ann, scaled_beta, hl_test,
                                                           ou_mean, ou_std, ou_diffusion_v,
                                                           recent_dev, recent_dev_scaled))
                scored_pairs[pair] = self.__score_coint(adf_test_statistic, self.adf_confidence_level, adf_critical_values)

                #if n_cointegrated == 10:
                # just checking the first 10 cointegrated pairs we find
                # otherwise it would take forever to check all the possible pairs
                # only for a single day;
                # logic to be fixed and made more efficient by: 1) having proper
                # clustering algorithm; 2) not running clustering and cointegration
                # everyday 3) taking best 10 pairs according to some score

                scored_pairs = OrderedDict(sorted(scored_pairs.items(), key=itemgetter(1), reverse = True))

        self.previous_cointegrated_pairs = current_cointegrated_pairs

        return current_cointegrated_pairs

    def __logged_lin_reg(self, x: DataFrame, y: DataFrame) -> Tuple[array, float]:

        log_x = x.applymap(lambda k: np.log(k))
        log_y = y.applymap(lambda k: np.log(k))

        results = LinearRegression(fit_intercept=False).fit(log_x, log_y)
        residuals = log_y - results.predict(log_x)  # e = y - y^
        beta = float(results.coef_[0])

        return np.array(residuals), beta

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

        residuals, beta = self.__logged_lin_reg(DataFrame(tau_vector), DataFrame(variance_delta_vector))

        # https://quant.stackexchange.com/questions/35513/explanation-of-standard-method-generalized-hurst-exponent

        return beta / 2

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

    def __score_coint(self,  t_stat: float, confidence_level: AdfPrecisions,  crit_values: Dict[str, float]):
        # currently scoring algorithm is only the l1 norm of adf_test_stat - confidence interval at the critical value we want to use
        delta = abs(t_stat - crit_values[confidence_level.value])
        return delta