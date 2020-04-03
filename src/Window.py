from datetime import date, timedelta

from src.DataRepository import DataRepository, DataLocations


class Window:

    def __init__(self,
                 window_start: date,
                 window_length: timedelta,
                 repository: DataRepository):

        self.window_start: date = window_start
        self.window_length: timedelta = window_length
        self.repository: DataRepository = repository

        # Window object contains information about timings for the window as well as SNP and ETF data for that period.
        self.window_end: date = self.window_start + self.window_length

        self.__get_window_data(self.window_start, self.window_end)

    def evolve(self):
        # Purely side-effectual; the function just mutates the object
        self.window_length += timedelta(days=1)
        self.window_end += timedelta(days=1)
        self.__get_window_data(self.window_start, self.window_end)
        return self

    def __get_window_data(self, start: date, end: date):
        self.etf_data = self.repository.get(DataLocations.ETFs, start, end)
        self.snp_data = self.repository.get(DataLocations.SNP, start, end)
