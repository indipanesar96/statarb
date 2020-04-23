import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def gbm_series(s0: float, period: int, sigma: float, mu: float, rand_st: int = 99) -> np.array:
    # drift 0.10, diffusion 0.30 (reasonable yearly drift and diffusion for risky asset)
    np.random.seed(rand_st)
    rand_series = np.random.normal(0, 1, period - 1)
    dt = 1 / 250
    # create stock price vector for X according to GBM model for stock prices
    s=[s0]
    st=s0
    for i in range(period-1):
        st = st * np.exp((mu - sigma ** 2 / 2) * dt + sigma * (dt ** 0.5) * rand_series[i])
        s.append(st)
    return np.array(s)


def ou_process(period: int, k: float, v: float, rand_st: int, u0: float = 0) -> np.array:
    np.random.seed(rand_st)
    rand_series = np.random.normal(0, 1, period - 1)
    dt = 1 / 250

    u = [u0]
    for i in range(period - 1):
        ut_lag = u[i]
        ut = ut_lag - k * ut_lag * dt + v * (dt ** 0.5) * rand_series[i]
        u.append(ut)
    return np.array(u)


def cointegrated_ts_generator(x: np.array, u: np.array, y0: float, beta: float, plot=False):
    """
    :param x: first series as np.array
    :param u: ou-error series as np.array
    :param y0: starting value for second series
    :param beta: coefficient of cointegration relationship
    :return: y: second series as np.array (cointegrated with x)
    """
    period = len(x)
    dt = 1 / 250
    x0 = x[0]
    y = [y0 if i == 0 else (y0 * (x[i] / x0)**beta * np.exp((u[i]-u[0]))) for i in range(period)]


    x = pd.DataFrame(np.array(x), columns=['FKSX'])
    y = pd.DataFrame(np.array(y), columns=['FKSY'])

    if plot:
        pd.concat([x, y], axis=1).plot(figsize=(12, 5))
        plt.show()

    return np.array(y)


if __name__ == '__main__':
    period = 1000
    x0 = 50
    y0 = 45
    sigma=.3
    mu=.1
    x = gbm_series(period=period, s0=x0, sigma=sigma, mu=mu)
    u = ou_process(period=period, k=250/15, v=0.3, rand_st=23)
    y = cointegrated_ts_generator(x, u, y0=y0, beta=1.2, plot=True)
