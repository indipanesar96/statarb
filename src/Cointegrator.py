from typing import Dict, Tuple
from typing import Optional
from math import log
import statsmodels.api as sm

import numpy as np
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.api import adfuller

from src.Window import Window
from src.DataRepository import DataRepository


##
class Cointegrator:

    def __init__(self, repository, adf_confidence_level, max_mean_rev_time, entry_z, exit_z, current_window: Window = None):
        self.repository: DataRepository = repository
        self.current_window: Optional[current_window]
        self.adf_confidence_level: str = adf_confidence_level
        self.max_mean_rev_time : float = max_mean_rev_time
        self.entry_z: float = entry_z
        self.exit_z:  float = exit_z
        self.invested = None



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

    def run_cointegrator(self, clustering_results: Dict[int, Tuple[str]]): #-> Dict[int, Tuple[str]]
        """
        iteratively test for cointegration for all the pairs within each cluster;
        return dictionary with a 2-element list of tickers as key, and a list of current holdings and current position (e.g. {["AAPL","GOOG"]: [beta, -1, "long"]})
        """
        # clustering_results should look like something similar:
        # {
        # 1: [('AAPL', 'GOOG'),('MSFT', 'GOOG'),('MSFT', 'AAPL')],
        # 2: [('AMGN', 'MMM')]
        # }
        cointegrated_pairs = []
        stock1_holding = 0
        stock2_holding = 0
        for cluster in clustering_results.values():
            for pair in cluster:
                # t1 = get_time_series(start_date: window_start, end_date: window_end, datatype: 'SNP', ticker: pair[0], feature: 'Last_Price')
                # t2 = get_time_series(start_date: window_start, end_date: window_end, datatype: 'SNP', ticker: pair[1], feature: 'Last_Price')
                t1 = self.current_window.get_data(universe='SNP', tickers = pair[0], features = 'Last_Price').tolist()
                t2 = self.current_window.get_data(universe='SNP', tickers = pair[1], features = 'Last_Price').tolist()


                cointegration_parameters = self.cointegration_analysis(t1, t2) # (X,Y)
                adf_test_statistic, adf_critical_values, hl_test, \
                hurst_exp, beta, latest_residual_scaled = cointegration_parameters
                zscore = latest_residual_scaled

                ######### Cointegration Check ###########
                #### check if adf_statistic less than self.adf_critical_values[adf_confidence_level] and return something
                #### if less, it means they are cointegrated of course

                ######### Half life check #############
                #### check if half life is less than self.max_mean_rev_time

                ######### Hurst exponent check #############
                #### check if half life is less than 0.5 --> if yes, then we are happy

                if adf_test_statistic <= adf_critical_values['5%'] and hl_test <= self.max_mean_rev_time and hurst_exp <= 0.5:
                    # stock1_holding = 0
                    # stock2_holding = 0
                    #stock_holding_list = []
                    # If we are not in the market
                    if self.invested is None:
                        if zscore < -self.entry_z:
                            # Long Entry
                            # Short stock1, long stock2
                            print("Opening Long: %s" % self.current_window)
                            stock1_holding = -beta
                            stock2_holding = 1
                            self.invested = "long"

                        elif zscore > self.entry_z:
                            # Short Entry
                            # Long stock1, short stock2
                            print("Opening Short: %s" % self.current_window)
                            stock1_holding = beta
                            stock2_holding = -1
                            self.invested = "short"

                    # If we are in the market
                    if self.invested is not None:
                        if self.invested == "long" and zscore < -self.entry_z:
                            # Holding Postion
                            print("Holding Long: %s" % self.current_window)
                            stock1_holding = -beta # or equal to the previous window -beta
                            stock2_holding = 1
                            self.invested = "long"
                        elif self.invested == "long" and zscore >= -self.exit_z:
                            # Close Position
                            print("Closing Long: %s" % self.current_window)
                            stock1_holding = 0
                            stock2_holding = 0
                            self.invested = None
                        elif self.invested == "short" and zscore > self.exit_z:
                            # Holding Position
                            print("Holding Short: %s" % self.current_window)
                            stock1_holding = beta # or equal to the previous window beta
                            stock2_holding = -1
                            self.invested = "short"
                        elif self.invested == "short" and zscore <= self.exit_z:
                            # Close Position
                            print("Closing Short: %s"% self.current_window)
                            stock1_holding = 0
                            stock2_holding = 0
                            self.invested = None
                else:
                    # Not conintegrated
                    print("Not Conintegrated: %s" % self.current_window)
                    stock1_holding = 0
                    stock1_holding = 0
                    self.invested = None
                cointegrated_pairs.append({list(pair): [stock1_holding, stock2_holding, self.invested]})
                # cointegrated_pairs.append([list(pair), today_signal]) # to be defined above
                # please make sure the logic is consistent and try some example values
        return cointegrated_pairs
        #return signals

    '''
    zscore represents the standardized residual error of the prediction at current window,
    while entry_z and exit_z represent thresholds for entering the market and exitting the 
    market at current window
    (entry_z and exit_z could be set mathematically, i.e., entry_z = two standard deviation of 
     the zscore, and exit_z = one standard deviation of the zscore)
    the rules are specified as follows:
    1. if zscore < - entry_z - Long the spread: 
    Short beta unit of stock1 and long 1 unit of stock2 
    2. if zscore > entry_z - Short the spread:
    Long beta unit of stock1 and short 1 unit of stock2
    3. if zscore >= exit_z - Exit long: 
    Close all positions of stock1 and stock2 
    4. if zscore <= exit_z - Exit short:
    Close all positions of stock1 and stock2
    
    ###Kalman Filter
    '''




    '''
    # zscore = latest_residual_scaled (defined in cointegration_analysis)
    def Signals(self,z_score, beta, entry_z, exit_z, stock1, stock2):
        stock1_holding = 0
        stock2_holding = 0
        stock_holding_list = []
        for i in range(1, len(stock1)):
            if z_score[i] <= entry_z and z_score[i-1] >= entry_z and stock1_holding == 0:
                # Short stock1, long stock2
                stock1_holding = -1
                stock2_holding = beta
                #short_price = stock1[i]
            elif z_score[i] >= -entry_z and z_score[i-1] <= -entry_z and stock1_holding == 0:
                # Long stock1, short stock2
                stock1_holding = 1
                stock2_holding = -beta
                #short_price = stock2[i]
            elif ((z_score[i-1] > exit_z and z_score[i] < exit_z) or (z_score[i-1] < -exit_z and z_score[i] >= -exit_z)):#or (abs(z_score[i] > limit)) and stock1_holding != 0: (Risk Management?)
                # Close Position
                stock1_holding = 0
                stock2_holding = 0

            stock_holding_list.append([stock1_holding, stock2_holding])

        return stock_holding_list


        #return #signal
    '''
    '''
    def z_score_trade(self, zscore):
        #
        Determine whether to trade if the entry or exit zscore
        threshold has been exceeded.
        #
        # If we are not in the market
        if self.invested is None:
            if zscore < -self.entry_z:
                # Long
                print("Go Long")
                self.go_long_units()
                self.invested = 'long'
            elif zscore > self.entry_z:
                # Short
                print("Go Short")
                self.go_short_units()
                self.invested = 'short'
        # If we already in the market
        if self.invested is not None:
            if self.invested == 'long' and zscore >= -self.exit_z:
                print("Close Long")
                self.go_short_units()
                self.invested = None
            elif self.invested == 'short' and zscore <= self.exit_z:
                print("Close Short")
                self.go_long_units()
                self.invested == None
    '''

    def cointegration_analysis(self, X, Y):
        """
        perform ADF test, Half-life and Hurst on pair of price time series
        return ADF test, ADF critical values for difference confidence levels,
        average time of mean reversion (half-life), Hurst exponent, beta,
        list containing 1. last-day residual, 2. scaler function to scale last-day residual
        (this is going to be useful for signal generation once we decide the thresholds)
        """
        # do cointegration regression of log-prices time series
        log_x = [log(i) for i in X]
        log_y = [log(i) for i in Y]
        #log_x = X.applymap(lambda k: np.log(k))
        #log_y = Y.applymap(lambda k: np.log(k))

        #results = LinearRegression().fit(log_x, log_y)
        #residuals = log_y - results.predict(log_x)  # e = y - y^
        #beta = float(results.coef_[0])
        model = sm.OLS(log_y, log_x).fit()
        beta = float(model.params[0])
        residuals = np.asarray(log_y) - beta * np.asarray(log_x)

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
        residual_scaler.fit(residuals.reshape(-1, 1))
        latest_residual_scaled = residual_scaler.transform(latest_residual.reshape(-1, 1))
        return adf_test_statistic, adf_critical_values, hl_test, hurst_exp, beta, latest_residual_scaled.tolist()[0][0]

    def half_life_test(self, residuals):
        """
        Calculates the half life of the residuals to check average time of mean reversion
        """
        # calculate the vector of lagged residuals
        lagged_residuals = residuals[:-1]  # independent variable
        delta_residuals = (residuals[1:] - lagged_residuals)  # dependent variable

        # do regression of delta residuals against lagged residuals
        results = LinearRegression().fit(lagged_residuals.reshape(-1, 1), delta_residuals.reshape(-1, 1))
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
        variance_delta_vector = [value if value != 0 else 1e-10 for value in variance_delta_vector]
        #  regress (10-base log of) variance_delta_vector against tau_vector
        results = LinearRegression().fit(np.log10(tau_vector).reshape(-1, 1), np.log10(variance_delta_vector).reshape(-1, 1))

        reg_coef = float(results.coef_[0])

        # return the calculated hurst exponent (regression coefficient divided by 2 as per formula)
        # if interested, see explanation here:
        # https://quant.stackexchange.com/questions/35513/explanation-of-standard-method-generalized-hurst-exponent

        return reg_coef / 2
