from pandas import DataFrame as Df
from src.Executor import Executor
from pandas import DataFrame as Df
from typing import Dict, Tuple
import statsmodels.api as sm
from statsmodels.tsa.api import adfuller
import numpy as np

class Cointegrator:

    def __init__(self, executor: Executor):
        self.executor = executor

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

    def run_cointegration_analysis(self,
                                   clustering_results : Dict[int, Tuple[str]] ,
                                   cointegration
                                   ) -> Dict[int, Tuple[str]]:
        pass

    def cointegration_analysis_rough(self, Y, X):
        # compute log prices and lag-log prices for last 60 days
        log_y = np.array(np.log(Y[-120:]))
        log_x = np.array(np.log(X[-120:]))

        lagged_log_y = np.array(np.log(Y[-121:-1]))
        lagged_log_x = np.array(np.log(X[-121:-1]))

        log_returns_y = log_y - lagged_log_y
        log_returns_x = log_x - lagged_log_x

        # add vector of 1s to account for intercept in regression
        x = sm.add_constant(log_returns_x)

        # do cointegration regression of "verticalized" vectors
        model = sm.OLS(log_returns_y.reshape(-1,1), x.reshape(-1,1))
        results = model.fit()
        residuals = results.resid

        # do Augmented-Dickey Fuller test and save p-value
        adf_results = adfuller(residuals)
        adf_p_value = adf_results[1]


        # call half_life_test function on residuals vector
        hl_test = half_life_test(residuals)

        # call hurst_exponent_test function on residuals vector



    def half_life_test(self, residuals):
        """
        Calculates the half life of the residuals to check average time of mean reversion
        """
        # calculate the vector of lagged residuals
        lagged_residuals = residuals[:-1]
        delta_residuals = residuals[1:] - lagged_residuals
        regressors = sm.add_constant(lagged_residuals)

        # do regression of "verticalized" delta residuals against lagged residuals
        model = sm.OLS(delta_residuals.reshape(-1, 1), regressors.reshape(-1, 1))
        results_1 = model.fit()
        pi = results_1.params[1]

        HL_test = np.log(2)/ (-pi)
        return HL_test

    def hurst_exponent_test(self, residuals):
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
        return results_2[0] /2

