# need to implement announcement gap for fundamental data

import yfinance as yf
from src.util.Tickers import SnpTickers


class yf_ticker:
	def __init__(self, ticker, financials, info):
		self.ticker = ticker
		self.financials = financials
		self.info = info

if __name__ == '__main__':
	ticker_list = [e.value for e in SnpTickers]
	data = []
	for ticker in ticker_list:
		print(ticker)
		yf_session = yf.Ticker(ticker)
		financials = yf_session.financials
		bs = yf_session.get_balance_sheet
		get_cashflow()
		info = yf_session.info
		ticker_class = yf_ticker(ticker = ticker, financials = financials, info = info)
		data.append(ticker_class)

	import pickle
	with open('/Users/Simon-CWG/Documents/SIF_git/git/src/util/fundamental_snp', 'wb') as f:
		pickle.dump(obj = data, file = f )

	with open('/Users/Simon-CWG/Documents/SIF_git/git/src/util/fundamental_snp', 'rb') as f:
		data = pickle.load(file = f )

	arrive = False
	for ticker in ticker_list:
		if arrive == False:
			if ticker != 'SO':
				continue
			else:
				arrive = True

		print(ticker)
		yf_session = yf.Ticker(ticker)
		financials = yf_session.financials
		info = yf_session.info
		ticker_class = yf_ticker(ticker=ticker, financials=financials, info=info)
		data.append(ticker_class)

	from src.util.Tickers import SnpTickers
	import pandas as pd
	SnpTickers
	df = pd.DataFrame()
	start = False
	for index, ticker in enumerate(data):
		print(index)
		print(ticker.ticker)
		financials = ticker.financials.transpose()
		interest = financials['Interest Expense']
		income = financials['Net Income']
		revenue = financials['Total Revenue']
		if not start:
			df[ticker.ticker+' interest_to_revenue'] = interest / revenue
			df[ticker.ticker+' income_to_revenue'] = income / revenue
			start = True
		else:
			df_temp = pd.DataFrame()
			df_temp[ticker.ticker+' interest_to_revenue'] = interest / revenue
			df_temp[ticker.ticker + ' income_to_revenue'] = income / revenue
			df = df.join(df_temp, how = 'outer')
		df.to_csv('/Users/Simon-CWG/Documents/SIF_git/git/src/util/fundamental_snp.csv')