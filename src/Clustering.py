from typing import Tuple, List, Set
import pandas as pd
from pandas import DataFrame
from collections import OrderedDict


class Clustering:

    #when we already have a position on some pair (bought on dat t)
        #they dont need to be considered in the clusterign analysis for t+1
        #go straight to cointegration analysis

    @classmethod
    def cluster(cls, data: Tuple[DataFrame]) -> OrderedDict[int: Tuple[str]]:

        pass
