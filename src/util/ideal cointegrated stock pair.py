import numpy as np
import pandas as pd
import math
import statsmodels
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.api import adfuller

# just set the seed for the random number generator
np.random.seed(99)

# Generate daily log returns (i.e., log differences for consecutive days closing price)
# for approximately 4 years (250 trading days per year)
standard_normal_vector = np.random.normal(0, 1, 1000)

# initialize stock price vector at 50, drift 0.10 (reasonable yearly drift for risky asset,
# to be estimated in real case), diffusion 0.30 (reasonable yearly volatility for risky asset,
# be estimated in real case)
sigma = 0.30
mu = 0.01

# if unit is one year (consistent with order of magnitude of mu and sigma) , then day= 1/250
dt = 1/250

X = [50]
X_t = X[0]

# create stock price vector for X
for i in range(1000):
    X_t = X_t * math.exp ((mu - sigma**2/2)*dt + sigma* (dt**0.5) * standard_normal_vector[i])
    X.append(X_t)

# plot stuff
X = pd.Series(np.array(X), name='X')
X.plot(figsize=(12,5))
plt.show()

###### defining specs for Yt ########
# initialize stock price vector at 45, beta 1.2, alpha 0.003
Y = [45]
Y_t = Y[0]
beta = 1.2
alpha = .0001
dt = 1 / 250

###### defining specs of OU ########
# speed of mean-reversion for OU process followed by residuals:
k = 250 / 15  # means that avg time of mean reversion is 15 days

# diffusion v
v = 0.3

###### simulating OU #######
np.random.seed(23)
standard_normal_vector_2 = np.random.normal(0, 1, 1000)
U = [0]
for i in range(1000):
    U_t_lag = U[i]
    U_t = U_t_lag - k * U_t_lag * dt + v * (dt ** 0.5) * standard_normal_vector_2[i]
    U.append(U_t)

# create stock price vector for Y
for i in range(1000):
    X_0 = X[0]
    X_t = X[i + 1]
    Y_t = Y[0] * (X_t / X_0) ** beta * math.exp(alpha * dt * (i + 1) + U[i])
    Y.append(Y_t)

# plot stuff
Y = pd.Series(np.array(Y), name='Y')
pd.concat([X, Y], axis=1).plot(figsize=(12, 5))
plt.show()

#calculate log price and log return
log_y = np.array(np.log(Y)).reshape(-1,1)
log_x = np.array(np.log(X)).reshape(-1,1)

y = np.array([log_y[i+1]-log_y[i] for i in range(len(log_y)-1)]).reshape(-1,1)
x = np.array([log_x[i+1]-log_x[i] for i in range(len(log_x)-1)]).reshape(-1,1)
x_ = sm.add_constant(x) #add column of 1s to account for intercept

model = sm.OLS(y, x_)
results = model.fit()
results.summary()

results.params[1]

