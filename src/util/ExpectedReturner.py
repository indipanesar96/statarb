from src.util.FakeCointegratedPair import gbm_series, ou_process, cointegrated_ts_generator
from src.util.PairReturnBuilder import signal_builder, pair_ret_builder
import numpy as np


def expected_returner(alpha, beta, mu_rx_ann, sigma_rx_ann, hl, v, xf, yf, recent_dev,  #0.075
                      res_m, res_std, max_mean_rev_time: int = 10):

    # probably need a fix and esimate sigma of ou vasicek through ml
    mu_rp_list = []
    sigma_rp_list = []
    for i in range(1000):
        x = gbm_series(s0=xf, period=max_mean_rev_time+1, sigma=sigma_rx_ann, mu=mu_rx_ann, rand_st=i)
        u = ou_process(period=max_mean_rev_time+1, k=250 / (2 * hl), v=v, u0=recent_dev, rand_st=i + 1000)
        y = cointegrated_ts_generator(x, u, y0=yf, beta=beta, alpha=alpha)
        u_scaled = (u - res_m) / res_std
        signal_vect = signal_builder(u_scaled)
        rp_temp = pair_ret_builder(x, y, signal_vect, beta)
        rp =np.array([])
        for ret in rp_temp:
            if ret ==0:
                break
            rp = np.append(rp, ret)
        #print(rp)
        mu_rp_ann = 250 * np.mean(rp)
        sigma_rp_ann = 250 ** 0.5 * np.std(rp)
        print("portf ret:", mu_rp_ann, ", stdv:", sigma_rp_ann)
        mu_rp_list.append(mu_rp_ann)
        sigma_rp_list.append(sigma_rp_ann)

    return np.mean(mu_rp_list), np.mean(sigma_rp_list)


if __name__ == "__main__":
    '''
    suppose we estimated the following from cointegration regression:
    alpha=0.01, beta=1.2, sigma_rx_ann = 0.3, mu_rx_ann = 0.1, hl=7.5 days, v=0.35, xf = 35, yf = 23
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
    xf = 50
    yf = 45
    res_m = 0
    res_std = 0.035
    recent_dev = 0.071

    mom_rp = expected_returner(alpha, beta, mu_rx_ann, sigma_rx_ann, hl, v, xf, yf, recent_dev, res_m, res_std)
    print("expected 1-year return of the considered pair is:", mom_rp[0], "\n",
          "expected 1-year stdv of the considered pair is:", mom_rp[1])
