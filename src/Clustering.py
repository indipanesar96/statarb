import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


class Clustering:

    def __init__(self, data):
        self.data = data

    def dbscan(self) -> OrderedDict[int, Tuple[str]]:
        '''
        return a dict {str: list of tuples}
        key: cluster number Cx, x=1,2,...,n
        value:  a list of tuples of the pairs in the same cluster [(1,3),(1,6)...]
        '''
        X = StandardScaler().fit_transform(self.data)
        dbscan = DBSCAN(min_samples=2).fit(X)
        labels = dbscan.labels_
        core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
        core_samples_mask[dbscan.core_sample_indices_] = True

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

        tickers = ['SPY', 'VTI', 'MMM', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADBE', 'AMD', 'AAP']
        clusters = {}
        pairs = []
        for i in itertools.combinations(dbscan.core_sample_indices_, 2):
            pair = (tickers[i[0]], tickers[i[1]])
            pairs.append(pair)
        clusters['C0'] = pairs
        return clusters

    def kmeans(self) -> OrderedDict[int, Tuple[str]]:
        pass

    def optics(self) -> OrderedDict[int, Tuple[str]]:
        pass
