import pandas as pd
import os
from scipy.stats import t
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# return in %
print(os.getcwd())
data = pd.read_csv("src/log.csv")
rt = data['return']
sns.distplot(rt)
plt.show()
t_param = t.fit(rt)
daily_var_5pt = t.ppf(q=0.05, df=t_param[0], loc=t_param[1], scale=t_param[2])
daily_var_1pt = t.ppf(q=0.01, df=t_param[0], loc=t_param[1], scale=t_param[2])
print("daily value at risk (5%): ", round(daily_var_5pt,2),"%")
print("daily value at risk (5%): ", round(daily_var_1pt,2),"%")