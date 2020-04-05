import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


class Clustering:

    #when we already have a position on some pair (bought on dat t)
        #they dont need to be considered in the clusterign analysis for t+1
        #go straight to cointegration analysis

    #@classmethod
    #def cluster(cls, data: Tuple[DataFrame]) -> OrderedDict[int: Tuple[str]]:
    #    pass


    def __init__(self, data):
        '''
        the data should be a dataframe with rows as the tickers and columns as the features
        '''
        self.data = data
        self.data_length = len(data)

    def dbscan(self, min_samples = 2):
        '''
        return a dict {str: list of tuples}
        key: cluster number Cx, x=1,2,...,n
        value:  a list of tuples of the pairs in the same cluster [(1,3),(1,6)...]
        '''
        X = StandardScaler().fit_transform(self.data)
        dbscan = DBSCAN(min_samples=min_samples).fit(X)
        self.dbscan_labels = labels = dbscan.labels_
        core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
        self.dbscan_core = dbscan.core_sample_indices_
        self.dbscan_core_length = len(dbscan.core_sample_indices_)
        core_samples_mask[self.dbscan_core] = True

        unique_labels = set(labels)
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
        for k, col in zip(unique_labels, colors):
            if k == -1:
                col = [0, 0, 0, 1]
            class_member_mask = (labels == k)

            xy = X[class_member_mask & core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)

            xy = X[class_member_mask & ~core_samples_mask] # binary one's complement
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

        #tickers = ['SPY', 'VTI', 'MMM', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADBE', 'AMD', 'AAP']
        clusters = {}
        pairs = []
        for i in itertools.combinations(dbscan.core_sample_indices_, 2):
            pair = (tickers[i[0]], tickers[i[1]])
            pairs.append(pair)
        clusters['C0'] = pairs
        return clusters

# copy this part
centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(n_samples=50, centers=centers, cluster_std=0.4,
                            random_state=0)
#X = StandardScaler().fit_transform(X)
df = pd.DataFrame(X)
# from Clustering import Clustering
clustering = Clustering(df)
cluster_dict = clustering.dbscan()
print(cluster_dict)
# copy this part
