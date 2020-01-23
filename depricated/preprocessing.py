import numpy as np
import pandas as pd
import bs4 as bs
import requests


def get_snp_500_tickers(extra_tickers=[]):
    """
    Wiki seems to be stale so also using slicknotes
    extra_tickers = other tickers you want to add
    """
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    resp2 = requests.get('https://www.slickcharts.com/sp500')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    soup2 = bs.BeautifulSoup(resp2.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    table2 = soup2.find('table', {'class': 'table table-hover table-borderless table-sm'})
    wiki_tickers = []
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        wiki_tickers.append(ticker)

    for row in table2.findAll('tr')[1:]:
        ticker = row.findAll('td')[2].text
        tickers.append(ticker)

    all_tickers = np.unique(tickers + wiki_tickers).tolist()
    tickers += extra_tickers
    all_tickers += extra_tickers

    return tickers, all_tickers


def get_nyse_tickers(extra_tickers=[], extra_companies=[]):
    """
    Gets a list of NYSE tickers from a website that seems to update the data yearly
    extra = extra tickers - must be a list otherwise function will error out
    """
    resp = requests.get(
        'https://pkgstore.datahub.io/core/nyse-other-listings/nyse-listed_csv/data/3c88fab8ec158c3cd55145243fe5fcdf/nyse-listed_csv.csv')
    all_data = resp.text.split('\r\n')
    all_data = [x for x in all_data if x != '']
    ticker_data, company_data = [x.split(',')[0] for x in all_data[1:] if '$' not in x], [x.split(',')[1] for x in
                                                                                          all_data[1:]]
    # removing $ as indicates preferred stocks which are not on yahoo finance
    ticker_data += extra_tickers
    company_data += extra_companies
    return ticker_data, company_data


def get_nasdaq_tickers(extra_tickers=[], extra_companies=[]):
    """
    Gets list of all NASDAQ stock exchange tickers
    Data is updated yearly
    extra_tickers- other tickers you want to include
    extra_companies - names of other companies
    both extras must be lists
    """
    resp = requests.get(
        'https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv')
    all_data = resp.text.split('\r\n')  # split into list of rows
    all_data = [row for row in all_data if row != '']  # remove empty rows
    ticker, company = [x.split(',')[0] for x in all_data[1:]], [x.split(',')[1] for x in
                                                                all_data[1:]]  # 1: to remove headers
    ticker += extra_tickers
    company += extra_companies
    return ticker, company


def main():
    tick_snp = get_snp_500_tickers()[1]  # pull all - change 1 to 0 to get current 500 listed
    tick_nyse = get_nyse_tickers(tick_snp)[0]  # this is to pull the ticker data only, get company data by changing to 1
    tick_nasdaq = get_nasdaq_tickers(tick_nyse)[0]
    tickers = np.unique(tick_nasdaq).tolist()
    tickers = [x.strip('\n') for x in tickers]
    df = pd.DataFrame(tickers)
    df.to_csv('C:/Users/tyehu/PycharmProjects/statarb/resources/sandp_nasdaq_nyc.csv', index=False, header=False) # remove indexed columns and rows so just get the tickers
    return df
