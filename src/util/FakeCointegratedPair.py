import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def cointegrated_pair_generator(sigma=0.3, mu=0.1, X_0=50,
                                Y_0=45, alpha=0.01, beta=1.2,
                                k=250 / 15, v=0.3, window=1000, seed=99):
    # just set the seed for the random number generator
    np.random.seed(seed)

    # Generate daily log returns (i.e., log differences for consecutive days closing price)
    # for approximately 4 years (250 trading days per year)
    standard_normal_vector = np.random.normal(0, 1, 1000)

    # initialize stock price vector at 50, drift 0.10 (reasonable yearly drift for risky asset,
    # to be estimated in real case), diffusion 0.30 (reasonable yearly volatility for risky asset,
    # be estimated in real case)
    sigma = sigma
    mu = mu

    # if unit is one year (consistent with order of magnitude of mu and sigma) , then day= 1/250
    dt = 1 / 250

    X = [X_0]
    X_t = X[0]

    # create stock price vector for X according to GBM model for stock prices
    for i in range(window):
        X_t = X_t * np.exp((mu - sigma ** 2 / 2) * dt + sigma * (dt ** 0.5) * standard_normal_vector[i])
        X.append(X_t)

    ###### defining specs for Yt ########
    # initialize stock price vector at 45, beta 1.2, alpha 0.0001
    Y = [Y_0]
    Y_t = Y[0]
    beta = beta
    alpha = alpha
    dt = 1 / 250

    ###### defining specs of OU ########
    # speed of mean-reversion for OU process followed by residuals:
    k = k  # if speed k = 250/15, it means that avg time of mean reversion is 15/250 years = 15 days

    # diffusion v
    v = 0.3

    ###### simulating OU #######
    np.random.seed(23)
    standard_normal_vector_2 = np.random.normal(0, 1, window)
    U = [0]
    for i in range(window):
        U_t_lag = U[i]
        U_t = U_t_lag - k * U_t_lag * dt + v * (dt ** 0.5) * standard_normal_vector_2[i]
        U.append(U_t)

    # create stock price vector for Y using Avellanada specification
    for i in range(window):
        X_0 = X[0]
        X_t = X[i + 1]
        Y_t = Y[0] * (X_t / X_0) ** beta * np.exp(alpha * dt * (i + 1) + U[i])
        Y.append(Y_t)

    X = pd.DataFrame(np.array(X), columns=['FKSX'])
    Y = pd.DataFrame(np.array(Y), columns=['FKSY'])
    U = pd.DataFrame(np.array(U), columns=['U'])

    return X, Y, U


if __name__ == '__main__':
    X, Y, U = cointegrated_pair_generator(sigma=0.9, mu=0.1, X_0=50,
                                          Y_0=45, alpha=0.01, beta=1.2,
                                          k=250 / 15, v=0.3, window=1000, seed=99)

    pd.concat([X, Y], axis=1).plot()
    plt.show()
