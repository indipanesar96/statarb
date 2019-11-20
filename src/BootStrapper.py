from TickerData import TickerData
from datetime import date
from Plotter import Plotter
from typing import Set, List, Tuple
import yfinance as yf
import sys

import matplotlib.pyplot as plt

# should probably use an enum class here
single_stock_tickers: Set[str] = ('MMM', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADBE', 'AMD', 'AAP', 'AES', 'AMG',
                                  'AFL', 'A', 'APD', 'AKAM', 'ALK', 'ALB', 'ARE', 'ALXN', 'ALGN', 'ALLE', 'AGN', 'ADS',
                                  'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AAL', 'AEP', 'AXP',
                                  'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'ADI', 'ANSS', 'ANTM', 'AON',
                                  'AOS', 'APA', 'AIV', 'AAPL', 'AMAT', 'APTV', 'ADM', 'ARNC', 'ANET', 'AJG', 'AIZ',
                                  'ATO', 'T', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'BKR', 'BLL', 'BAC', 'BK', 'BAX',
                                  'BBT', 'BDX', 'BRK', 'BBY', 'BIIB', 'BLK', 'HRB', 'BA', 'BKNG', 'BWA', 'BXP', 'BSX',
                                  'BMY', 'AVGO', 'BR', 'BF', 'CHRW', 'COG', 'CDNS', 'CPB', 'COF', 'CPRI', 'CAH', 'KMX',
                                  'CCL', 'CAT', 'CBOE', 'CBRE', 'CBS', 'CDW', 'CE', 'CELG', 'CNC', 'CNP', 'CTL', 'CERN',
                                  'CF', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'XEC', 'CINF', 'CTAS', 'CSCO',
                                  'C', 'CFG', 'CTXS', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL', 'CMCSA', 'CMA', 'CAG',
                                  'CXO', 'COP', 'ED', 'STZ', 'COO', 'CPRT', 'GLW', 'CTVA', 'COST', 'COTY', 'CCI', 'CSX',
                                  'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE', 'DAL', 'XRAY', 'DVN', 'FANG', 'DLR',
                                  'DFS', 'DISCA', 'DISCK', 'DISH', 'DG', 'DLTR', 'D', 'DOV', 'DOW', 'DTE', 'DUK', 'DRE',
                                  'DD', 'DXC', 'ETFC', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'EMR', 'ETR',
                                  'EOG', 'EFX', 'EQIX', 'EQR', 'ESS', 'EL', 'EVRG', 'ES', 'RE', 'EXC', 'EXPE', 'EXPD',
                                  'EXR', 'XOM', 'FFIV', 'FB', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FE', 'FRC', 'FISV',
                                  'FLT', 'FLIR', 'FLS', 'FMC', 'F', 'FTNT', 'FTV', 'FBHS', 'FOXA', 'FOX', 'BEN', 'FCX',
                                  'GPS', 'GRMN', 'IT', 'GD', 'GE', 'GIS', 'GM', 'GPC', 'GILD', 'GL', 'GPN', 'GS', 'GWW',
                                  'HAL', 'HBI', 'HOG', 'HIG', 'HAS', 'HCA', 'PEAK', 'HP', 'HSIC', 'HSY', 'HES', 'HPE',
                                  'HLT', 'HFC', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HPQ', 'HUM', 'HBAN', 'HII', 'IEX',
                                  'IDXX', 'INFO', 'ITW', 'ILMN', 'IR', 'INTC', 'ICE', 'IBM', 'INCY', 'IP', 'IPG', 'IFF',
                                  'INTU', 'ISRG', 'IVZ', 'IPGP', 'IQV', 'IRM', 'JKHY', 'JEC', 'JBHT', 'SJM', 'JNJ',
                                  'JCI', 'JPM', 'JNPR', 'KSU', 'K', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KLAC', 'KSS',
                                  'KHC', 'KR', 'LB', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LEG', 'LDOS', 'LEN', 'LLY',
                                  'LNC', 'LIN', 'LKQ', 'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MAC', 'M', 'MRO', 'MPC',
                                  'MKTX', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MKC', 'MXIM', 'MCD', 'MCK', 'MDT', 'MRK',
                                  'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MHK', 'TAP', 'MDLZ', 'MNST', 'MCO',
                                  'MS', 'MOS', 'MSI', 'MSCI', 'MYL', 'NDAQ', 'NOV', 'NTAP', 'NFLX', 'NWL', 'NEM',
                                  'NWSA', 'NWS', 'NEE', 'NLSN', 'NKE', 'NI', 'NBL', 'JWN', 'NSC', 'NTRS', 'NOC', 'NLOK',
                                  'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'ORLY', 'OXY', 'OMC', 'OKE', 'ORCL', 'PCAR',
                                  'PKG', 'PH', 'PAYX', 'PYPL', 'PNR', 'PBCT', 'PEP', 'PKI', 'PRGO', 'PFE', 'PM', 'PSX',
                                  'PNW', 'PXD', 'PNC', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PSA',
                                  'PHM', 'PVH', 'QRVO', 'PWR', 'QCOM', 'DGX', 'RL', 'RJF', 'RTN', 'O', 'REG', 'REGN',
                                  'RF', 'RSG', 'RMD', 'RHI', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'CRM', 'SBAC', 'SLB',
                                  'STX', 'SEE', 'SRE', 'SHW', 'SPG', 'SWKS', 'SLG', 'SNA', 'SO', 'LUV', 'SPGI', 'SWK',
                                  'SBUX', 'STT', 'SYK', 'STI', 'SIVB', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO',
                                  'TPR', 'TGT', 'TEL', 'FTI', 'TFX', 'TXN', 'TXT', 'TMO', 'TIF', 'TWTR', 'TJX', 'TSCO',
                                  'TDG', 'TRV', 'TRIP', 'TSN', 'UDR', 'ULTA', 'USB', 'UAA', 'UA', 'UNP', 'UAL', 'UNH',
                                  'UPS', 'URI', 'UTX', 'UHS', 'UNM', 'VFC', 'VLO', 'VAR', 'VTR', 'VRSN', 'VRSK', 'VZ',
                                  'VRTX', 'VIAB', 'V', 'VNO', 'VMC', 'WAB', 'WMT', 'WBA', 'DIS', 'WM', 'WAT', 'WEC',
                                  'WCG', 'WFC', 'WELL', 'WDC', 'WU', 'WRK', 'WY', 'WHR', 'WMB', 'WLTW', 'WYNN', 'XEL',
                                  'XRX', 'XLNX', 'XYL', 'YUM', 'ZBH', 'ZION', 'ZTS')

start_date: date = date(2018, 1, 1)
end_date: date = date(2019, 1, 1)

# close_prices = yf.download(['WCG', 'WFC'], str(start_date), str(end_date)).Close
# msft = yf.Tickers('MSFT')

n_stocks = 10
single_stock_data: List[TickerData] = list(
    TickerData(ticker, start_date, end_date) for ticker in single_stock_tickers[:n_stocks - 1]
)

spy: TickerData = TickerData('SPY', start_date, end_date)  # https://www.etf.com/SPY
vti: TickerData = TickerData('VTI', start_date, end_date)  # https://www.etf.com/VTI#overview
ubio: TickerData = TickerData('UBIO', start_date, end_date)  # https://www.etf.com/UBIO
soxl: TickerData = TickerData('SOXL', start_date, end_date)  # https://www.etf.com/SOXL

#for i in single_stock_data:
#    print(i.ticker)
data_to_be_plotted: List[TickerData] = [spy, vti] + single_stock_data

plt.figure()

for d in data_to_be_plotted:
    print(d.ave_return, d.std_of_returns)
    plt.scatter(d.ave_return, d.std_of_returns, label=d.ticker)

plt.ylim(-1, 1)
plt.title("Ave return vs ave volatility")
plt.legend(loc = r"best")
plt.tight_layout()
plt.show()
# Plotter.plot(data_to_be_plotted)
