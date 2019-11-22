from pandas import DataFrame as Df
from src.Executor import Executor
from pandas import DataFrame as Df
from typing import Dict, Tuple

class Cointegrator:

    def __init__(self, executor: Executor):
        self.executor = executor

    def check_holdings(self, current_holdings: Df):
        '''
        Receives a dataframe of current holdings to check if the pairs are no longer co integrated

        If all of the current holdings are still cointegrated, do nothing except print a log line and return inital df
        If any current holdings fail cointegration, calls the executor to close a position

        :param current_holdings:
        :return:
        '''

        '''
        do some cointegration test here
        
        if nothing failed:
            return the current holdings, unedited
            
        else:
            return self.executor.close_positon(('aapl', 'msft'), current_holdings)
            return new dataframe of holdings with the one position closed
        '''



        pass

    def run_cointegration_analysis(self,
                                   clustering_results : Dict[int, Tuple[str]] ,
                                   cointegration
                                   ) -> Dict[int, Tuple[str]]:
        pass
