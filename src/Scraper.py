import yfinance as yf
from datetime import date


class Scraper:
    @staticmethod
    def scrape(ticker: str, start_date: date, end_date: date):
        '''
        :return: returns a tuple of returns and cum returns
        '''
        close_prices = yf.download(ticker, str(start_date), str(end_date)).Close
        returns = close_prices.pct_change().rename(ticker + " Return")
        cum_return = returns.cumsum().rename(ticker + " Cumulative Return")
        return returns, cum_return
