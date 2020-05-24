# need to implement announcement gap for fundamental data

import yfinance as yf
from src.util.Tickers import SnpTickers
import pickle
import datetime
import pandas as pd

'''
DONE:
v1
interest_to_revenue
income_to_revenue
v2
Size
ROE
Book to Market
Dividend Yield
Leverage

TODO:
Capital Turnover
Earning to Price
Investment to Income
Profit Margin

ROA
'''


class yf_ticker:
	def __init__(self, ticker, financials, bs, cf, info, close):
		self.ticker = ticker
		self.financials = financials
		self.bs = bs
		self.cf = cf
		self.info = info
		self.close = close

skip_list = ['ARNC','ODFL','REGN','WCG']

def get_ticker_data(ticker):
	yf_session = yf.Ticker(ticker)
	financials = yf_session.financials
	bs = yf_session.balance_sheet
	cf = yf_session.cashflow
	price = {}
	for date in financials.columns:
		next_day = date.date() + datetime.timedelta(days=1)
		price_df = yf_session.history(period='1d', start=next_day, end=next_day)
		lag_count = 0
		while price_df.shape[0] == 0:
			lag_count += 1
			print(next_day)
			next_day = next_day + datetime.timedelta(days=-1)
			price_df = yf_session.history(period='1d', start=next_day, end=next_day)
			if lag_count >= 30:
				skip_list.append(ticker)
				break
		if price_df.shape[0] == 0:
			continue
		price[date] = price_df['Close'].values
	close = pd.DataFrame(price, index=['Close']).transpose()
	info = yf_session.info
	ticker_class = yf_ticker(ticker=ticker, financials=financials, bs = bs, cf = cf, info=info, close=close)
	return ticker_class


if __name__ == '__main__':
	ticker_list = [e.value for e in SnpTickers]
	data = []
	for ticker in ticker_list:
		print(ticker)
		data.append(get_ticker_data(ticker))

	with open('/Users/Simon-CWG/Documents/SIF_git/git/src/util/fundamental_snp_0524_part', 'wb') as f:
		pickle.dump(obj = data[390:], file = f )



	with open('/Users/Simon-CWG/Documents/SIF_git/git/src/util/fundamental_snp_0524', 'rb') as f:
		data = pickle.load(file = f )

	ticker_list = [e.value for e in SnpTickers]
	arrive = False
	for ticker in ticker_list:
		if arrive == False:
			if ticker != 'WDC':
				continue
			else:
				arrive = True

		print(ticker)
		data.append(get_ticker_data(ticker))

	from src.util.Tickers import SnpTickers
	import pandas as pd
	df = pd.DataFrame()
	start = False
	no_div_count = 0
	no_common_stock_count = 0
	no_treasury_stock_count = 0
	for index, ticker in enumerate(data):
		print(index)
		print(ticker.ticker)
		financials = ticker.financials.transpose()
		bs = ticker.bs.transpose()
		cf = ticker.cf.transpose()
		close = ticker.close['Close']
		interest = financials['Interest Expense']
		income = financials['Net Income']
		revenue = financials['Total Revenue']
		try:
			common_stock = bs['Common Stock']
		except:
			no_common_stock_count+=1
			continue
		try:
			treasury_stock = bs['Treasury Stock']
		except:
			no_treasury_stock_count += 1
			treasury_stock = 0
		size = close * (common_stock + treasury_stock)
		equity = bs['Total Stockholder Equity']
		if 'Dividends Paid' not in cf.columns:
			no_div_count += 1
			dividend = 0
		else:
			dividend = cf['Dividends Paid']
		debt = bs['Total Liab']

		if not start:
			df[ticker.ticker+' interest_to_revenue'] = interest / revenue
			df[ticker.ticker+' income_to_revenue'] = income / revenue
			df[ticker.ticker + ' size'] = size
			df[ticker.ticker + ' book_to_market'] = equity / size
			df[ticker.ticker + ' ROE'] = income / equity
			df[ticker.ticker + ' dividend yield'] = dividend / size
			df[ticker.ticker + ' leverage'] = debt / equity
			start = True
		else:
			df_temp = pd.DataFrame()
			df_temp[ticker.ticker + ' interest_to_revenue'] = interest / revenue
			df_temp[ticker.ticker + ' income_to_revenue'] = income / revenue
			df_temp[ticker.ticker + ' size'] = size
			df_temp[ticker.ticker + ' book_to_market'] = equity / size
			df_temp[ticker.ticker + ' ROE'] = income / equity
			df_temp[ticker.ticker + ' dividend yield'] = dividend / size
			df_temp[ticker.ticker + ' leverage'] = debt / equity
			df = df.join(df_temp, how = 'outer')
		df.to_csv('/Users/Simon-CWG/Documents/SIF_git/git/src/util/fundamental_snp.csv')