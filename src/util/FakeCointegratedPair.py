from typing import Any, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def gbm_series(s0: float, period: int, sigma: float = 0.3, mu: float = 0.1, rand_st: int = 99)->np.array:
    # drift 0.10, diffusion 0.30 (reasonable yearly drift
    # and diffusion for risky asset, to be estimated in real case)
    np.random.seed(rand_st)
    standard_normal_vector = np.random.normal(0, 1, period-1)

    # if unit is one year (consistent with order of magnitude of mu and sigma), then day= 1/250
    dt = 1 / 250
    s = [s0]
    st = s[0]

    # create stock price vector for X according to GBM model for stock prices
    for i in range(period-1):
        st = st * np.exp((mu - sigma ** 2 / 2) * dt + sigma * (dt ** 0.5) * standard_normal_vector[i])
        s.append(st)
    return np.array(s)

def ou_process(period:int, k:float =250 / 15, v:float=0.3, rand_st:int=23)->np.array:
    np.random.seed(rand_st)
    standard_normal_vector = np.random.normal(0, 1, period-1)
    dt = 1 / 250
    u = [0]
    for i in range(period-1):
        ut_lag = u[i]
        ut = ut_lag - k * ut_lag * dt + v * (dt ** 0.5) * standard_normal_vector[i]
        u.append(ut)
    return np.array(u)

def cointegrated_pair_generator(x: np.array, u:np.array, y0:float, beta:float =1.2, alpha:float=0.01, plot=False):
    '''
    :param x: first series as np.array
    :param u: ou-error series as np.array
    :param y0: starting value for second series
    :param k: speed of mean reversion for OU-process; if k = 250/15 => avg time mean reversion is 15/250 years = 15 days
    :param v: diffusion of OU-process
    :return: y: second series as np.array (cointegrated with x)
    '''
    period = len(x)
    dt = 1 / 250
    y = [y0]

    # create stock price vector for y using Avellanada specification
    for i in range(period-1):
        x0 = x[0]
        xt = x[i + 1]
        yt = y[0] * (xt / x0) ** beta * np.exp(alpha * dt * (i + 1) + u[i])
        y.append(yt)

    x = pd.DataFrame(np.array(x), columns=['FKSX'])
    y = pd.DataFrame(np.array(y), columns=['FKSY'])

    if plot:
        pd.concat([x, y], axis=1).plot(figsize=(12, 5))
        plt.show()

    return np.array(x), np.array(y)


if __name__ == '__main__':
    period = 1000
    x0=210
    y0=170
    x = gbm_series(period=period, s0=x0)
    u = ou_process(period=period)
    x,y = cointegrated_pair_generator(x, u, y0=y0, plot=True)


