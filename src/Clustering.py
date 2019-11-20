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

    def dbscan(self):
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

            xy = X[class_member_mask & ~core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

        plt.title('Clustering')
        plt.show()


X = np.array([[-0.00023248654202514808, -0.0002619913655537728, -0.0007353652382561316,
               0.000927608494770463, -1.6138875340238285e-05, 0.002550805923079642,
               -0.00023947155846431434, -0.0010109697057888135, 0.0012156648131022442,
               0.0028625379820238846, 0.0017762952097903223],
              [0.010804362321813862, 0.010659257923463653, 0.015054761602112271,
               0.014041917637427424, 0.022177242755590354, 0.03000175909230052,
               0.01473112795795041, 0.023506840970410097, 0.022376491785068883,
               0.039604644320766706, 0.019937860959241452]])
X = (X*100).transpose()
df = pd.DataFrame(X)
clustering = Clustering(df)
clustering.dbscan()
