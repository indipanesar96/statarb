import pandas as pd
import os
from scipy.stats import t
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# value at risk
print(os.getcwd())
data = pd.read_csv("src/log.csv")
rt = data['return'] # return in %
sns.distplot(rt)
plt.show()
t_param = t.fit(rt)
daily_var_5pt = t.ppf(q=0.05, df=t_param[0], loc=t_param[1], scale=t_param[2])
daily_var_1pt = t.ppf(q=0.01, df=t_param[0], loc=t_param[1], scale=t_param[2])
print("daily value at risk (5%): ", round(daily_var_5pt,2),"%")
print("daily value at risk (5%): ", round(daily_var_1pt,2),"%")

# prob of reaching drawdown threshold
def maximumDrawdown(rets: np.array):
    cum_rets = np.nancumprod(rets + 1)
    mdd = 0
    peak = cum_rets[0]
    for ret in cum_rets:
        if ret > peak: peak = ret
        dd = (peak - ret) / peak
        if dd > mdd: mdd = dd
    return mdd

def rets_builder(days):
        return t.rvs(df=t_param[0], loc=t_param[1], scale=t_param[2], size=days)/100 # % to decimal

max_dds = [0.05, 0.10]
years_measured_in_days = [250, 500, 750]
table = np.zeros((3,2))
for i, days in enumerate(years_measured_in_days):
    for j, max_dd in enumerate(max_dds):
        dd_array = np.array([maximumDrawdown(rets_builder(days)) for i in range(10000)])
        table[i,j] = len(dd_array[dd_array >= max_dd]) / len(dd_array)

print(pd.DataFrame(table, index=years_measured_in_days, columns = max_dds))