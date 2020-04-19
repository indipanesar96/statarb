from src.util.FakeCointegratedPair import gbm_series, ou_process, cointegrated_pair_generator
from src.util.PairReturnBuilder import decision_maker, signaler, pair_return_builder
import numpy as np

def expected_returner(alpha, beta, mu_rx_ann, sigma_rx_ann, hl, v, xf, yf):
    mu_rp_list = []
    for i in range(100):
        x = gbm_series(s0=xf, period=250, sigma=sigma_rx_ann, mu=mu_rx_ann, rand_st=i)
        u = ou_process(period=250, k = 250/(2*hl), v=v, rand_st=i+100)
        u = (u - np.mean(u))/np.std(u)
        x, y = cointegrated_pair_generator(x, u, y0=yf, beta=beta, alpha=alpha)
        signal_vect = signaler(u)
        rp = pair_return_builder(x, y, signal_vect, beta)
        mu_rp = np.mean(rp)
        mu_rp_list.append(mu_rp)

    return np.mean(mu_rp_list)




if __name__=="__main__":
    '''
    suppose we estimated the following from cointegration regression:
    alpha=0.01
    beta=1.2
    sigma_rx_ann = 0.3
    mu_rx_ann = 0.1
    hl=7.5 days
    v=0.35 (rmse of residuals of half-life regression)
    xf = 35
    yf = 23
    from these parameters, we can estimate future paths for x,y,u over next 250 trading days
    REMEMBER TO CORRECT OU TO BE SCALED APPROPRIATELY USING SCALER FROM RESIDUAL REGRESSION (need to ad as param).
    What is done now is inaccurate
    '''
    alpha = 0.01
    beta = 1.2
    sigma_rx_ann = 0.3
    mu_rx_ann = 0.1
    hl = 7.5
    k = 250 / 2 / hl
    v = 0.35
    xf = 35
    yf = 23

    mu_rp = expected_returner(alpha, beta, mu_rx_ann, sigma_rx_ann, hl, v, xf, yf)
    print("expected 1-year return of the considered pair is:", mu_rp)