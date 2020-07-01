import numpy as np
import pandas as pd

pd.options.display.max_columns = None
pd.options.display.max_rows = None
from sklearn.cluster import DBSCAN
from src.DataRepository import Universes
from src.util.Features import Features
from datetime import date


class Clusterer:

    def __init__(self, clusters=None):
        # To store the clusters of tickers we found the previous day. On day 1 this will be None.
        # Same as return type of DBscan Method
        # Type:
        #    return a dict {int: list of ticker couples} like the following:
        # {
        # 1: [('AAPL', 'GOOG'),('MSFT', 'GOOG'),('MSFT', 'AAPL')],
        # 2: [('AMGN', 'MMM')]
        # }
        #    key: cluster number Cx, x=1,2,...,n

        self.cluster_history = []

    def dbscan(self, today: date, min_samples, eps=None, window=None):
        self.window = window

        clustering_features = [Features.INTRADAY_VOL, Features.VOLUME]
        snp_to_cluster_on = window.get_data(Universes.SNP, None, clustering_features)
        etf_to_cluster_on = window.get_data(Universes.ETFs, None, clustering_features)
        try:
            data_to_cluster_on = pd.concat([snp_to_cluster_on, etf_to_cluster_on], axis=1)
        except ValueError as _:
            print(f"Got different lengths for etfs and snp for clustering data, taking intersection...")

            common_dates = sorted(set(snp_to_cluster_on.index).intersection(set(etf_to_cluster_on.index)))

            data_to_cluster_on = pd.concat([
                snp_to_cluster_on.loc[snp_to_cluster_on.index.intersection(common_dates)].drop_duplicates(keep='first'),
                etf_to_cluster_on.loc[etf_to_cluster_on.index.intersection(common_dates)].drop_duplicates(keep='first')
            ], axis=1)

        # to now we have a single number per column,
        # (averaging over time dim) so can now compare cross-sectionally, rank-wise

        mean_of_features_over_time = data_to_cluster_on.mean(axis=0)

        ranked_mean_intraday_vols = mean_of_features_over_time.loc[:, Features.INTRADAY_VOL].rank(ascending=True)
        ranked_mean_volumes = mean_of_features_over_time.loc[:, Features.VOLUME].rank(ascending=True)

        rank_normaliser = lambda val, series: ((val - 0.5 * (max(series) - min(series)))) / (
                0.5 * (max(series) - min(series)))

        normed_volume_ranks = ranked_mean_volumes.apply(lambda val: rank_normaliser(val, ranked_mean_volumes))
        normed_intraday_vol_ranks = ranked_mean_intraday_vols.apply(
            lambda val: rank_normaliser(val, ranked_mean_intraday_vols))

        X = pd.concat([normed_volume_ranks, normed_intraday_vol_ranks], axis=1)

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

        self.tickers = normed_volume_ranks.index
        labels = dbscan.labels_
        self.unique_labels = set(labels)
        self.n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        self.n_noise = list(labels).count(-1)
        self.noise = np.where(labels == -1)[0]

        clusters = {}

        for cluster_num in self.unique_labels:
            tickers_in_this_cluster = X.index[np.where(labels == cluster_num)[0]]

            clusters[cluster_num] = tickers_in_this_cluster.values

        return clusters

# if __name__ == '__main__':
#
#     X = pd.concat([normed_volume_ranks, normed_intraday_vol_ranks], axis=1)
#
#     plt.figure()
#     plt.scatter(x=X.loc[:, 0], y=X.loc[:, 1])
#     plt.xlabel(str(X.columns[0]))
#     plt.ylabel(str(X.columns[1]))
#     plt.tight_layout()
#     plt.show()
