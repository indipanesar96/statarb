import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

#from src.Window import Window


class Clusterer:

    def __init__(self, data, clusters=None):

        # To store the clusters of tickers we found the previous day. On day 1 this will be None.
        # Same as return type of DBscan Method
        # Type:
        #    return a dict {int: list of ticker couples} like the following:
        # {1: [('AAPL', 'GOOG'),('MSFT', 'GOOG'),('MSFT', 'AAPL')]}
        #    key: cluster number Cx, x=1,2,...,n

        self.data = data
        self.data_length = len(data)
        self.clusters = clusters
        self.cluster_history = [None]


    def dbscan(self, eps, min_samples):#, window: Window):
        # replace data with window.etf_data or similarly for SNP

        X = StandardScaler().fit_transform(self.data)
        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        self.dbscan_labels = labels = dbscan.labels_
        core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
        core_samples_mask[dbscan.core_sample_indices_] = True
        self.dbscan_core_indices = dbscan.core_sample_indices_
        self.dbscan_core_length = len(dbscan.core_sample_indices_)
        self.dbscan_core_mask = core_samples_mask

        self.unique_labels = unique_labels = set(labels)
        self.n_clusters = n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        self.n_noise = n_noise = list(labels).count(-1)
        self.noise = np.where(labels==-1)[0]

        # something

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

    def kmeans(self, data_denoised, n_clusters, random_state=0):
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data_denoised)
        self.data_denoised = data_denoised
        self.data_denoised_length = len(data_denoised)
        self.kmeans_labels = km_labels = kmeans.labels_
        #unique_labels = set(km_labels)
        clusters = {}
        for j in range(n_clusters):
            pairs = []
            for i in itertools.combinations(np.where(km_labels == j)[0], 2):
                pair = (i[0], i[1])
                pairs.append(pair)
            clusters['C' + str(j)] = pairs
        return clusters


    def optics(self):
        pass


    def plot(self):
        #X_0 = self.data_denoised[np.where(self.kmeans_labels==0)[0]]
        plt.figure(figsize=(20, 20))

        plt.subplot(211)
        for i in range(self.n_clusters):
            W = self.data_denoised[np.where(self.kmeans_labels==i)[0]]
            plt.scatter(W[:,0], W[:,1])
        plt.title("KMeans")

        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(self.unique_labels))]
        plt.subplot(212)
        for k, col in zip(self.unique_labels, colors):
            if k == -1:
                col = [0, 0, 0, 1]
            class_member_mask = (self.dbscan_labels == k)

            xy = X[class_member_mask & self.dbscan_core_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)

            xy = X[class_member_mask & ~self.dbscan_core_mask] # binary one's complement
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

        plt.title("DBSCAN")
        plt.show()


# Simone you may refer to the following code to see how to use the class
centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(n_samples=50, centers=centers, cluster_std=0.4,
                            random_state=0)
#X = StandardScaler().fit_transform(X)
df = pd.DataFrame(X)
# from Clustering import Clustering
clustering = Clusterer(df)
dbscan_clusters = clustering.dbscan(eps=0.35, min_samples=3)
print("DBSCAN Clusters: ", dbscan_clusters, "\n")
print("DBSCAN Labels: ", clustering.dbscan_labels, "\n")
print("Noise: ", clustering.noise, "\n")
#print(clustering.dbscan_labels)
X_denoised = X[clustering.dbscan_core_mask]
#print(X_denoised[0])
kmeans_clusters = clustering.kmeans(X_denoised, 3)
print("KMEANS Clusters: ", kmeans_clusters, "\n")
print("KMEANS Labels: ", clustering.kmeans_labels, "\n")
#print(clustering.kmeans_labels)
clustering.plot()



# if __name__ == '__main__':
#
#     centers = [[1, 1], [-1, -1], [1, -1]]
#     X, labels_true = make_blobs(n_samples=50, centers=centers, cluster_std=0.4,
#                                 random_state=0)
#     X = StandardScaler().fit_transform(X)
#     clustering = Clusterer(X)
#     cluster_dict = clustering.DBScan()
#     print(cluster_dict)
