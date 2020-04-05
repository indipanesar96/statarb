import itertools

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

from src.Window import Window


class Clusterer:

    def __init__(self, clusters=None):

        # To store the clusters of tickers we found the previous day. On day 1 this will be None.
        # Same as return type of DBscan Method
        # Type:
        #    return a dict {int: list of ticker couples} like the following:
        # {1: [('AAPL', 'GOOG'),('MSFT', 'GOOG'),('MSFT', 'AAPL')]}
        #    key: cluster number Cx, x=1,2,...,n

        self.clusters = clusters
        self.cluster_history = [None]


    def DBScan(self, window: Window):
        # replace data with window.etf_data or similarly for SNP

        X = StandardScaler().fit_transform(self.data)
        dbscan = DBSCAN(min_samples=3).fit(X)
        labels = dbscan.labels_
        core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
        core_samples_mask[dbscan.core_sample_indices_] = True

        unique_labels = set(labels)
        n_clusters = len(unique_labels) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)  #why are we computing this? delete if non relevant


        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
        for k, col in zip(unique_labels, colors):
            if k == -1:
                col = [0, 0, 0, 1]
            class_member_mask = (labels == k)

            xy = X[class_member_mask & core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)

            xy = X[class_member_mask & ~core_samples_mask]  # binary one's complement
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

        plt.title('Estimated number of clusters: %d' % n_clusters)
        plt.show()

        # tickers = ['SPY', 'VTI', 'MMM', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADBE', 'AMD', 'AAP']
        clusters = {}
        for j in range(n_clusters):
            pairs = []
            for i in itertools.combinations(np.where(labels == j)[0], 2):
                pair = (i[0], i[1])
                pairs.append(pair)
            clusters['C' + str(j)] = pairs

        # some code here to update the class variables
        # self.cluster_history.append(clusters)
        # self.clusters =clusters

        return clusters

    def kmeans(self):
        pass

    def optics(self):
        pass



# if __name__ == '__main__':
#
#     centers = [[1, 1], [-1, -1], [1, -1]]
#     X, labels_true = make_blobs(n_samples=50, centers=centers, cluster_std=0.4,
#                                 random_state=0)
#     X = StandardScaler().fit_transform(X)
#     clustering = Clusterer(X)
#     cluster_dict = clustering.DBScan()
#     print(cluster_dict)
