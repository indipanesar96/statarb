from pandas import DataFrame as Df
from src.Executor import Executor
from pandas import DataFrame as Df
from typing import Dict, Tuple
import statsmodels.api as sm
from statsmodels.tsa.api import adfuller
import numpy as np

class Cointegrator:

    def check_holdings(self, current_holdings: Df):
        '''
        Receives a dataframe of current holdings to check if the pairs are no longer co integrated

        If all of the current holdings are still cointegrated, do nothing except print a log line and return inital df
        If any current holdings fail cointegration, calls the executor to close a position

        :param current_holdings:
        :return:
        '''

        '''
        do some cointegration test here
        
        if nothing failed:
            return the current holdings, unedited
            
        else:
            return self.executor.close_positon(('aapl', 'msft'), current_holdings)
            return new dataframe of holdings with the one position closed
        '''



        pass

    def run_cointegrator(self, clustering_results : Dict[int, Tuple[str]],) -> Dict[int, Tuple[str]]:
        """
        iteratively test for cointegration all the pairs within each cluster;
        return dictionary with a 2-element list of tickers as key, and a list
        """
        cointegrated_pairs = []
        for cluster in clustering_results.values():
            for pair in cluster:

                ## Call Thom's function with price column and convert to numpy arrays y, x
                # cointegration_parameters = self.cointegration_analysis(y, x)
                # cointegrated_pairs.append([list(pair),cointegration_parameters])
                pass
        pass


    def cointegration_analysis(self, Y, X):
        """
        perform ADF test, Half-life and Hurst on pair of price time series
        return ADF test p-value, average time of mean reversion, Hurst exponent, beta,
        list containing 1. last-day residual, 2. mean, 3. stdv of residual vector
        (this is going to be useful for signal generation once we decide the thresholds)
        """
        # do cointegration regression of twp price time series
        model = sm.OLS(Y[-200:], X[-200:])
        results = model.fit()
        residuals = np.array(results.resid)
        beta = results.params[1]

        # do Augmented-Dickey Fuller test and save p-value
        adf_results = adfuller(residuals)
        adf_p_value = adf_results[1]

        # call half_life_test function on residuals vector
        hl_test = half_life_test(residuals)

        # call hurst_exponent_test function on residuals vector
        hurst_exp = hurst_exponent_test(residuals)

        return adf_p_value, hl_test, hurst_exp, beta, [residuals[-1],np.mean(residuals), np.std(residuals)]

    def half_life_test(residuals):
        """
        Calculates the half life of the residuals to check average time of mean reversion
        """
        # calculate the vector of lagged residuals
        lagged_residuals = residuals[:-1]
        delta_residuals = (residuals[1:] - lagged_residuals)
        regressors = sm.add_constant(lagged_residuals)

        # do regression of delta residuals against lagged residuals
        model = sm.OLS(delta_residuals, regressors)
        results_1 = model.fit()
        pi = results_1.params[1]

        # calculate average time of mean reversion from average speed of mean reversion as per formula
        HL_test = np.log(2) / (-pi)

        return HL_test

    def hurst_exponent_test(residuals):
        """
        Returns the Hurst Exponent of the time series vector
        """
        # initialize empty vector for different lags indicated as tau
        tau_vector = []
        # initialize empty vector for variances of deltas characterized by different lags
        variance_delta_vector = []
        # Create the range of lag values
        lags = range(2, 100)

        #  Step through the different lags
        for lag in lags:
            #  produce deltas using residuals and respective n-lag
            delta_res = residuals[lag:] - residuals[:-lag]

            #  append the different lags into a vector
            tau_vector.append(lag)
            #  Calculate the variance of the delta and append it into a vector
            variance_delta_vector.append(np.var(delta_res))

        #  regress (log of) variance_delta_vector against tau_vector
        results_2 = np.polyfit(np.log10(np.asarray(tau_vector)),
                               np.log10(np.asarray(variance_delta_vector).clip(min=0.0000000001)),
                               1)
        # return the calculated hurst exponent (regression coefficient divided by 2 as per formula)
        return results_2[0] / 2

