from pandas import Series as Sr

class Filters:

    def __init__(self, data, threshold_sigma):
        self.data = data # historic data from which we calculate the history
        # volumes so we know what constitutes a shock)
        self.threshold_sigma = threshold_sigma #how many stdvs away from mean we classify a shock - to be perturbed

    def apply_volume_shock_filter(self, reversions):

        # gets a dictionary of reversions = {[ticker, ETFTicker]: [size of short, size of long]}
        # for i in reversions.iteritems():
        #     function call to determine volume shock state or not for each ticker, etf pair
        #             function returns tuple of booleans = states
        #
        #     if states.distinct().size == 2:
        #
        #         remove this key:value paor
        #         dictionary.drop(key:value pair)

        return reversions


    def __is_volume_shock(self, keyvaluepair):

        # vlumedataforticker : Sr  = self.data[keyvaluepair[key]].volume[daterange]
        # #daterange is t-375 days to t-125 days but check with paper
        # vlumedataforETFticker : Sr = self.data[keyvaluepair[etfticker]].volume[daterange]
        #
        # self.__get_mu_sigma(vlumedataforticker)
        #
        # # NEED TO FIND THE WINDOW OVER WHICH WE TAKE THE MEAN AND STD to compare to historic == 'current window'

        pass

    def __get_mu_sigma(self, tocker: Sr):
        mean = tocker.mean()
        std = tocker.std()
        return mean, std
