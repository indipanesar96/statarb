from typing import Dict, Tuple

import numpy as np
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.api import adfuller

from src.DataRepository import DataRepository

##
class Cointegrator:

    def __init__(self, repository):
        self.repository: DataRepository = repository

    def check_holdings(self, current_holdings: DataFrame):
        '''
        Receives a dataframe of current holdings to check if the pairs are no longer cointegrated

        If all of the current holdings are still cointegrated, do nothing except print a log line and return initial DataFrame
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

    def run_cointegrator(self, clustering_results: Dict[int, Tuple[str]], ) -> Dict[int, Tuple[str]]:
        """
        iteratively test for cointegration all the pairs within each cluster;
        return dictionary with a 2-element list of tickers as key, and a list
        """
        cointegrated_pairs = []
        for cluster in clustering_results.values():
            for pair in cluster:
                # t1 = whatever Simon's function is on pair[0] -->the first ticker in the pair
                # t2 = whatever Simon's function is on pair[1]-->the first ticker in the pair

                cointegration_parameters = self.cointegration_analysis(t1, t2)
                adf_test_statistic, adf_critical_values, hl_test, hurst_exp, beta = cointegration_parameters[:5]
                latest_residual, residual_scaler = cointegration_parameters[5][0], cointegration_parameters[5][1]

                ######### cointegration check ###########
                #### check if adf_statistic less than self.adf_critical_values[adf_confidence_level] and return something
                #### if less, it means they are cointegrated of course

                ######### Half life check #############
                #### check if half life is less than self.max_mean_rev_time

                ######### Hurst exponent check #############
                #### check if half life is less than 0.5 --> if yes, then we are happy

                cointegrated_pairs.append([list(pair), cointegration_parameters])

                # please make sure the logic is consistent and try some example values



    # need X, Y as one-column dataframes and NOT pd.Series as input
    def cointegration_analysis(self, X, Y):
        """
        perform ADF test, Half-life and Hurst on pair of price time series
        return ADF test, ADF critical values for difference confidence levels,
        average time of mean reversion (half-life), Hurst exponent, beta,
        list containing 1. last-day residual, 2. scaler function to scale last-day residual
        (this is going to be useful for signal generation once we decide the thresholds)
        """
        X, Y = np.array(X), np.array(Y)
        # do cointegration regression of two price time series
        results = LinearRegression().fit(X, Y)
        residuals = Y - results.predict(X)  # e = y - y^
        beta = float(results.coef_[0])

        # do Augmented-Dickey Fuller test and save adf_statistic, adf_critical_values
        adf_results = adfuller(residuals)
        adf_test_statistic, adf_critical_values = adf_results[0], adf_results[4]
        # critical values are in the following dictionary form:
        # {'1%': -3.4304385694773387,
        #  '5%': -2.8615791461685034,
        #  '10%': -2.566790836162312}

        # call half_life_test function on residuals to compute half life
        hl_test = self.half_life_test(residuals)

        # call hurst_exponent_test function on residuals to compute hurst exponent
        hurst_exp = self.hurst_exponent_test(residuals)

        # save latest residual and scaler function in case we want to scale it
        latest_residual = residuals[-1]
        residual_scaler = StandardScaler()
        residual_scaler.fit(residuals)

        return adf_test_statistic, adf_critical_values, hl_test, hurst_exp, beta, [latest_residual, residual_scaler]

    def half_life_test(self, residuals):
        """
        Calculates the half life of the residuals to check average time of mean reversion
        """
        # calculate the vector of lagged residuals
        lagged_residuals = residuals[:-1]  # independent variable
        delta_residuals = (residuals[1:] - lagged_residuals)  # dependent variable

        # do regression of delta residuals against lagged residuals
        results = LinearRegression().fit(lagged_residuals, delta_residuals)
        pi = float(results.coef_[0])

        # calculate average time of mean reversion from average speed of mean reversion as per formula
        HL_test = np.log(2) / (-pi)

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

        #  step through the different lags
        for lag in lags:
            #  produce deltas using residuals and respective n-lag
            delta_res = residuals[lag:] - residuals[:-lag]

            #  append the different lags into a list
            tau_vector.append(lag)
            #  Calculate the variance of the delta and append it into a list
            variance_delta_vector.append(np.var(delta_res))

        # avoid 0 values for variance_delta_vector
        variance_delta_vector = [value if value != 0 else 1e-10 for elem in variance_delta_vector]
        #  regress (10-base log of) variance_delta_vector against tau_vector
        results = LinearRegression().fit(np.log10(tau_vector).reshape(-1, 1), np.log10(variance_delta_vector))

        reg_coef = float(results.coef_[0])

        # return the calculated hurst exponent (regression coefficient divided by 2 as per formula)
        # if interested, see explanation here:
        # https://quant.stackexchange.com/questions/35513/explanation-of-standard-method-generalized-hurst-exponent

        return reg_coef / 2
