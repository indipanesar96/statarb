import pandas as pd
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import yfinance as yf
import numpy as np
from src.Performance import get_performance_stats


with open('every7days.txt') as f:
    lines = f.readlines()

lines = [line.rstrip() for line in lines]
got_today =  False
got_nums =  False
todays_date = datetime.datetime.now().date()
index = pd.date_range(todays_date, periods=1, freq='D')
port = pd.DataFrame(columns=["Total Capital", "Cum Returns"], index=index)

for idx, line in enumerate(lines):

    if line.startswith("Today"):
        today_line = line.split(":")[1]
        date_string = today_line.split("\t")[0].split(" ")[1].strip()
        date = datetime.datetime.strptime(date_string.strip(), "%Y-%m-%d").date()
        got_today =  True

    # 'Total Capital: 100523.5201\tCum Return: 0.005222'
    if line.startswith("Total Capital"):
        split1 = line.split(":")
        total_capital = float(split1[1].split("\t")[0].split(" ")[1].strip())
        cum_return = float(split1[-1])
        got_nums = True

    if got_nums == True and got_today == True:
        port.loc[date] = [total_capital, cum_return]
        got_today =  False
        got_nums = False

port = port.dropna()
port = port.sort_index()

sp = yf.download("^GSPC", start=min(port.index), end=max(port.index))[["Adj Close"]]["Adj Close"]

# port.index = [i.date() for i in port.index]
sp.index = [i.date() for i in sp.index]

common_dates = sorted(set(sp.index).intersection(set(port.index)))
sp = sp[common_dates]
port = port[port.index.isin(common_dates)]

sp = np.log(sp) - np.log(sp.iloc[0])

normalise = lambda series: series / (series[0] if int(series[0]) != 0 else 1.0)

port_ret = np.log(port['Total Capital']) - np.log(port['Total Capital'].iloc[0])

SR = port_ret.mean() / port_ret.std() * np.sqrt(252)

print(SR)

plt.figure(1, figsize=(10, 7))
plt.plot(port.index, port['Cum Returns'], label ="Stat Arb")
plt.plot(port.index, normalise(sp), label=r"SnP 500")
plt.title("Trading Everyday")
plt.legend(loc=r"best")
plt.xlabel("Date")
plt.ylabel("Cumulative Returns")
plt.tight_layout()

plt.show()

date_parser = lambda x: pd.datetime.strptime(x, '%d/%m/%Y')
yearly_to_daily = lambda x: x / 365
pct_to_num = lambda x: x / 100
tbill = pd.read_csv("../resources/3m_tbill_daily.csv", index_col='date', date_parser=date_parser)

tbill = tbill.applymap(yearly_to_daily)
tbill = tbill.applymap(pct_to_num)

tbill.index += timedelta(1)
tbill_mean = tbill.loc[tbill.index.intersection(port.index)].mean().values

print(get_performance_stats(port, tbill_mean))