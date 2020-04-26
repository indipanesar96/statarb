from src.util.FakeCointegratedPair import gbm_series, ou_process, cointegrated_ts_generator
from src.util.PairReturnBuilder import signal_builder, pair_ret_builder
from src.Cointegrator import CointegratedPair
import numpy as np


def expected_returner(cointegrated_pair : CointegratedPair, xf, yf, max_mean_rev_time: int = 30):

    beta = cointegrated_pair.scaled_beta
    mu_rx_ann = cointegrated_pair.mu_x_ann
    sigma_rx_ann = cointegrated_pair.sigma_x_ann
    hl = cointegrated_pair.hl
    recent_dev = cointegrated_pair.recent_dev_scaled
    ou_mean = cointegrated_pair.ou_mean
    ou_std = cointegrated_pair.ou_std
    ou_diffusion_v = cointegrated_pair.ou_diffusion_v

    # probably need a fix and esimate sigma of ou vasicek through ml
    mu_rp_list = []
    sigma_rp_list = []
    for i in range(500):
        x = gbm_series(s0=xf, period=max_mean_rev_time+1, sigma=sigma_rx_ann, mu=mu_rx_ann, rand_st=i)
        u = ou_process(period=max_mean_rev_time+1, k=250 * np.log(2)/ hl, v=ou_diffusion_v, u0=recent_dev, rand_st=i + 1000)
        y = cointegrated_ts_generator(x, u, y0=yf, beta=beta)
        u_scaled = (u - ou_mean) / ou_std
        signal_vect = signal_builder(u_scaled)
        rp_temp = pair_ret_builder(x, y, signal_vect, beta)
        rp =np.array([])
        for ret in rp_temp:
            if ret ==0:
                break
            rp = np.append(rp, ret)
        mu_rp_ann = 250 * np.mean(rp)
        sigma_rp_ann = 250 ** 0.5 * np.std(rp)
        #print("portf ret:", mu_rp_ann, ", stdv:", sigma_rp_ann)
        mu_rp_list.append(mu_rp_ann)
        sigma_rp_list.append(sigma_rp_ann)

    return np.mean(mu_rp_list), np.mean(sigma_rp_list)


if __name__ == "__main__":
    '''
    suppose we estimated the following from cointegration regression:
    alpha=0.01, beta=1.2, sigma_rx_ann = 0.3, mu_rx_ann = 0.1, hl=7.5 days, v=0.35, xf = 35, yf = 23
    from these parameters, we can estimate future paths for x,y,u over next 250 trading days
    What is done now is inaccurate
    '''
    beta = 1.2
    mu_rx_ann = 0.1
    sigma_rx_ann = 0.3
    xf = 50
    yf = 45
    hl = 7.5
    ou_mean = -0.017
    ou_std = 0.043
    ou_diffusion_v = 0.70
    recent_dev = 0.071

    mom_rp = expected_returner(beta, mu_rx_ann, sigma_rx_ann, hl, xf, yf, recent_dev,
                               ou_mean, ou_std, ou_diffusion_v)
    print("expected 1-year return of the considered pair is:", mom_rp[0], "\n",
          "expected 1-year stdv of the considered pair is:", mom_rp[1])
