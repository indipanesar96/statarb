import numpy as np
import pandas as pd

def maximumDrawdown(ret_series):
	"""
	Calculates maximum drawdown duration of the strategy
	Input :
			ret_series - return series of the strategy
	Return: mdd - maximum drawdown duration for the return series
	"""

	ret_series = np.array(ret_series)
	ret_series = ret_series / 100
	ret_series = 1 + ret_series
	cum_ret = np.cumprod(ret_series)
	mdd = 0
	peak = cum_ret[0]
	for x in np.array(cum_ret):
		if x > peak:
			peak = x
		dd = (peak - x) / peak
		if dd > mdd:
			mdd = dd

	return mdd

def get_performance_stats(prices, rf):
	# Number of business days in a year
	BUS_DAYS = 252

	# Pre-allocate empty dataframe for stats
	stats = pd.DataFrame(index=[0])


	Ret = prices.pct_change()

	# Returns (decimal form): (P_{t} - P_{t-1}) / P_{t-1}
	# Total Cumulative Return (decimal form): (P_{T} - P_{0}) / P_{0}
	# DataFrame.shape gives size ( [0] means across 1st dim, ie rows); equivalent of saying len(prices) )
	# DataFrame.shape gives size ( [0] means across 1st dim, ie rows); equivalent of saying len(prices) )

	lastIndex = prices.shape[0] - 1  # need - 1 since array referencing starts from 0
	P_Last = prices[lastIndex]
	stats['Tot Ret'] = (P_Last - prices[0]) / prices[0]  # (prices[ prices.shape[0]] / prices[0])-1 does same in 1 step
	stats['Avg Ret'] = Ret.mean() * BUS_DAYS
	stats['rfr'] = rf # .mean() * 365  # Note the convention for interbank rate is 365 days
	stats['Std'] = Ret.std() * np.sqrt(BUS_DAYS)  # sigma*sqrt(T)

	stats['SR'] = (stats['Avg Ret'] - stats['rfr']) / stats['Std']  # Sharpe Ratio

	stats['Skew'] = Ret.skew()  # For normal should be 0
	stats['Kurt'] = Ret.kurtosis()  # For normal should be 3

	stats['HWM'] = prices.max()  # returns max price or HIGH WATER MARK

	HWM_time = prices.idxmax()  # returns argument corresponding to max price (i.e. Timestamp,
	# e.g. Timestamp('2018-01-26 00:00:00'))

	stats['HWM date'] = HWM_time.date()  # converts Timestamp('2018-01-26 00:00:00') to
	# datetime.date(2018, 1, 26)

	# Maximum Drawdown - maximum loss from a peak to a trough of a portfolio, before a new peak is attained.
	# prices.cummax() returns a dataframe (date, CM_Price): cumulative max of prices going along the series
	# (i.e. monotonically increasing function)

	DD = prices.cummax() - prices  # get all Drawdowns: diffs between cumulative max price and current price
	end_mdd = DD.idxmax()  # get date of max Drawdown
	# maxDD = 888.6, argmax = Timestamp('2009-03-09 00:00:00')
	start_mdd = prices[:end_mdd].idxmax()  # get date of max price before trough ('2009-03-09 00:00:00')
	# prices[:end_mdd] - prices from starting time to end_mdd Timestamp
	# maxPrice = 1565.15, argmax = Timestamp('2007-10-09 00:00:00')

	# Maximum Drawdown defined here as POSITIVE proportional loss from peak (notation is sometimes NEGATIVE)

	stats['MDD'] = 1 - prices[end_mdd] / prices[start_mdd]  # (same as P_start - P_end) / P_start
	stats['Peak date'] = start_mdd.date()
	stats['Trough date'] = end_mdd.date()

	bool_P = prices[end_mdd:] > prices[start_mdd]  # True/False current price > price of DD peak

	if (bool_P.idxmax().date() > bool_P.idxmin().date()):

		stats['Rec date'] = bool_P.idxmax().date()  # date of first True occurrence, i.e. first time price
		# goes over price of DD peak#, ie fully recovered from DD

		stats['MDD dur'] = (stats['Rec date'] - stats['Peak date'])[
			0].days  # MDD duration in days from peak to recovery date
	else:
		stats['Rec date'] = stats[
			'MDD dur'] = 'Yet to recover'  # IF no True found anywhere in bool_P series, then idxmax
	# is date of 1st False of series (idxmin) - this is wrong! So as an
	# error check, we check if idxmax = idxmin. In that case the rec
	# date and mdd dur are not known as the DD peak has NOT been recovered yet

	# USEFUL TO ALSO REPORT COMPOUND GROWTH RATE, CALMAR RATIO
	# (ANNUAL AVG RETURN / MAX DD OVER LAST 36 MONTHS),
	# AND SORTINO RATIO

	return stats.T  # returns transpose of pandas DF