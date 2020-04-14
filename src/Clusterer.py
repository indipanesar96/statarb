import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.options.display.max_columns = None
pd.options.display.max_rows = None
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.DataRepository import Universes
from src.util.Features import Features


# from util.Tickers import SnpTickers
# from util.Features import SnpFeatures
# from DataRepository import Universes


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

        self.clusters = clusters
        self.cluster_history = [None]

    def average_over_time(self, window):

        data = window.get_data(Universes.SNP, None, None)

        averaged_over_time = data.mean().values.reshape(len(self.window.snp_live_tickers), len(Features))

        self.data_previously_clustered_on = averaged_over_time
        self.data_length = len(averaged_over_time)
        return averaged_over_time

    def dbscan(self, min_samples, eps=None, window=None):

        self.window = window
        self.tickers = window.snp_live_tickers

        flat_data = self.average_over_time(window)
        self.normalised = StandardScaler().fit_transform(flat_data)

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(self.normalised)

        self.dbscan_labels = labels = dbscan.labels_
        core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
        core_samples_mask[dbscan.core_sample_indices_] = True
        self.dbscan_core_indices = dbscan.core_sample_indices_
        self.dbscan_core_length = len(dbscan.core_sample_indices_)
        self.dbscan_core_mask = core_samples_mask

        self.unique_labels = set(labels)
        self.n_clusters = n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        self.n_noise = list(labels).count(-1)
        self.noise = np.where(labels == -1)[0]

        clusters = {}
        for j in range(n_clusters):
            pairs = []
            for i in itertools.combinations(np.where(labels == j)[0], 2):
                pair = (i[0], i[1])
                if window is not None:
                    pair = (self.tickers[i[0]], self.tickers[i[1]])
                pairs.append(pair)
            clusters[j] = pairs

        return clusters

    def kmeans(self, n_clusters, random_state=0):
        data_denoised = None
        if self.window == None:
            data_denoised = self.flat_data[self.dbscan_core_mask]
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data_denoised)
        self.data_denoised = data_denoised
        self.data_denoised_length = len(data_denoised)
        self.kmeans_labels = km_labels = kmeans.labels_
        clusters = {}
        for j in range(n_clusters):
            pairs = []
            for i in itertools.combinations(np.where(km_labels == j)[0], 2):
                pair = (i[0], i[1])
                pairs.append(pair)
            clusters[j] = pairs
        return clusters

    def plot(self):
        # X_0 = self.data_denoised[np.where(self.kmeans_labels==0)[0]]
        plt.figure(figsize=(20, 20))

        plt.subplot(211)
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(self.unique_labels))]
        for k, col in zip(self.unique_labels, colors):
            if k == -1:
                col = [0, 0, 0, 1]
            class_member_mask = (self.dbscan_labels == k)

            xy = self.flat_data[class_member_mask & self.dbscan_core_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)

            xy = self.flat_data[class_member_mask & ~self.dbscan_core_mask]  # binary one's complement
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)
        plt.title("DBSCAN")

        plt.subplot(212)
        for i in range(self.n_clusters):
            W = self.data_denoised[np.where(self.kmeans_labels == i)[0]]
            plt.scatter(W[:, 0], W[:, 1])
        plt.title("KMeans")

        plt.show()


if __name__ == '__main__':
    # Simone you may refer to the following code to see how to use the class
    clustering = Clusterer()
    dbscan_clusters = clustering.dbscan(eps=0.35, min_samples=3)
    print("DBSCAN Clusters: ", dbscan_clusters, "\n")
    print("DBSCAN Labels: ", clustering.dbscan_labels, "\n")
    print("Noise: ", clustering.noise, "\n")
    # print(clustering.dbscan_labels)
    kmeans_clusters = clustering.kmeans(clustering.n_clusters)
    print("KMEANS Clusters: ", kmeans_clusters, "\n")
    print("KMEANS Labels: ", clustering.kmeans_labels, "\n")
    # print(clustering.kmeans_labels)
    clustering.plot()
