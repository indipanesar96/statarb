# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 13:23:18 2019
f
@author: tyehu
"""

# Will try to make this into a bash script that can be run automatically

# 1) install bloomberg C++ API
# 2) merge C++ api to python path:
#    conda install -c conda-forge blpapi
# 3) import pdblp - use pip install pdblp
# 4) run bbcomm.exe in backgroud before this


import pdblp
import datetime as dt
import pandas as pd
import argparse  # allow user input
import glob  # iterate through fi


def get_bloomberg_data(stock_list, bbg_functions, start_date, end_date):
    con = pdblp.BCon(port=8194, debug=True)
    con.start()
    df = pd.DataFrame(con.bdh(stock_list, bbg_functions, start_date, end_date, long_data=True))
    return df


def get_dates(input_folder):
    try:
        max_dates = []
        for file in glob.glob(input_folder + '/*.csv'):  # iterate through all csv data files
            df = pd.read_csv(file)
            recent_date = max(df[['date']])  # uses output from initial file
            max_dates.append(recent_date)
        start_date = max(max_dates + dt.timedelta(days=1)).strftime('%Y%m%d')
    except Exception as _:  # if there is any error do this - assumes no data in folder
        start_date = dt.datetime((dt.datetime.today() - dt.timedelta(days=365 * 4)).year, 1, 1).strftime('%Y%m%d')
    end_date = (dt.datetime.today() - dt.timedelta(days=1)).strftime('%Y%m%d')  # end date is always yesterday
    return start_date, end_date


def get_all_data():
    """
    Inputs are CSV files with the ticker names in them
    get ticker names from preprocessing.py csv outputs
    pulls bloomberg data into dataframe with format:
    
            date         ticker    field         value
    0 2015-06-29  SPY US Equity  PX_LAST  2.054200e+02
    1 2015-06-29  SPY US Equity   VOLUME  2.026213e+08
    2 2015-06-30  SPY US Equity  PX_LAST  2.058500e+02
    3 2015-06-30  SPY US Equity   VOLUME  1.829251e+08
    """
    parser = argparse.ArgumentParser(description='bloomberg data extracter')
    parser.add_argument('-S', '--fileS', help='file with stock tickers', required=True)
    parser.add_argument('-E', '--fileE', help='file with ETF tickers', required=True)
    parser.add_argument('-EorB', '--EB', help='Equity or bond list', required=True)
    parser.add_argument('-o', 'dirO', help='folder containing all data', required=True)
    parser.add_argument('-F', '--listF',
                        help='list of extra bloomberg functions apart from price, volume, ebitda, enterprise value and asset value')
    parser.add_argument('-S', 'startdate', help='start_date', default='')
    parser.add_argument('-E', 'end_date', help='end date', default='')
    args = parser.parse_args()

    input_S = args.fileS
    input_E = args.fileE
    Equity_or_Bond = args.EB
    dirO = args.dirO
    extra_functions = args.listF
    start_date = args.start_date
    end_date = args.end_date

    ticker_list = pd.read_csv(input_S).tolist()
    # convert data into bloomberg terminology assumes data is US only

    if Equity_or_Bond not in ('Equity', 'Bond'):
        print('Please put Equity or Bond in -EorB')
    elif Equity_or_Bond == 'Equity':
        ticker_list = [ticker + ' US Equity' for ticker in ticker_list]
    else:
        ticker_list = [ticker + ' US Bond' for ticker in ticker_list]

    ETF_list = pd.read_csv(input_E).tolist
    ETF_list = [ETF_ticker + ' US Equity' for ETF_ticker in ETF_list]

    if start_date == '' and end_date == '':
        start_date, end_date = get_dates(dirO)
    else:
        pass

    function_list = ['LAST_PRICE', 'PX_OPEN', 'VOLUME', 'AVG_PX', 'PX_HIGH', 'PX_LOW', 'PX_ASK', 'PX_BID', 'LAST_PRICE',
                     'TO_EBITDA', 'PE_RATIO', 'ENTERPRISE_VALUE', 'ASSET_VAL'] + extra_functions

    underlying_df = get_bloomberg_data(ticker_list, function_list, start_date, end_date)
    ETF_df = get_bloomberg_data(ETF_list, function_list, start_date, end_date)
    underlying_df.to_csv(dirO + '/underlying_bloomberg_data' + end_date + '.csv')
    ETF_df.to_csv(dirO + '/ETF_bloomberg_data' + end_date + '.csv')

    return underlying_df, ETF_df
