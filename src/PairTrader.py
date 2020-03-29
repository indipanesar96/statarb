import datetime
from datetime import date, timedelta
from typing import Optional, List

from pandas import DataFrame
from src.Clusterer import Clusterer
from src.Cointegrator import Cointegrator
from src.DataRepository import DataRepository
from src.Filters import Filters
from src.Window import Window

'''
This project now runs in a virtual environment (3.7), for module/python version controlling (better for when we handover to next year's team).
Go to settings (ctrl + alt + s or cmd + ,) and ensure youre using the virtual env (under Project Interpreter)

The most basic of PyCharm shortcuts you may/may not already know that'll make your lives easier when navigating:
    - cmd + B (b for browse) or cmd+click on an object to take you to its definition (ctrl + B/click for windows)
    - cmd + [ = last cursor position (ctrl + alt + left arrow)
    - cmd + ] = next cursor position (ctrl + alt + right arrow)
    - cmd + k (k for Kommit, ie Commit) to commit (ctrl for windows)
    - cmd + shift + k to push a commit up to the sky (ctrl for windows)
    - cmd + t (t for updaTe) to pull down the latest commits from the sky (ctrl for windows)
    - shift + F6 (with fn key for mac) to do a project-level refactor
    - alt + enter is your friend - pulls up a useful cursor-context menu
    - cmd + alt + L = autoformat (ctrl for windows) [DO THIS BEFORE EVERY COMMIT PLS]
    - cmd + alt + O = optimise imports (ctrl for windows) [DO THIS BEFORE EVERY COMMIT PLS]

./depricated needs to go; I'll remove it in a week or so (and delete this line after). Take out any code you may and 
implement it in asap please.

Bits of python you may not have seen before:
    - method name preceeded with __ is so a subclass doesn't override a private method of a superclass
        don't have to actually worry about this as I don't think we have any inheritance yet, it's just good practice 
         e.g. https://stackoverflow.com/questions/70528/why-are-pythons-private-methods-not-actually-private
    - DataLocations is an example of an Enum class. More info: https://www.tutorialspoint.com/enum-in-python 
    - The strong typing (anywhere you see variable_name: variable_type, eg 'List', 'Tuple', 'Optional' etc from the typing module)
        aren't actually required, theyre just useful within PyCharm to make sure you don't shove a string into an int (or worse) 
         and throw an AttributeError or TypeError at runtime. 
        
If there's any code you can't figure out after some googling remember PyCharm's annotate feature. Right click on the line number
(in fact, any line of any checked in file) you're struggling with and click 'Annotate'. It'll tell you who checked it into the repo. Ask them directly. 
Failing that, contact me.

Of course if there's any code I (I make a lot of mistakes) or anyone else has written that you think is incorrect/could be made better, 
do contact them/change it yourself - this is a learning experience for us all. If it turns out it was correct all along you can use some git magic 
to get it back. Once it's commited it's never lost.
'''


class PairTrader:

    def __init__(self,
                 start_date: date = datetime.date(2008, 1, 1),
                 window_length: timedelta = timedelta(days=90),
                 end_date: Optional[date] = None):
        # If end_date is None, run for the entirety of the dataset
        # Window is the lookback period (from t=-window_length-1 to t=-1 (yesterday) over which we analyse data
        # to inform us on trades to make on t=0 (today). We assume an expanding window for now.

        self.repository = DataRepository()
        inital_window = Window(window_start=start_date,
                               window_length=window_length,
                               repository=self.repository)

        self.start_date: date = start_date
        self.window_length: timedelta = window_length
        self.end_date: date = end_date

        # Portfolio might need to be its own object later, cross that bridge when we come to it
        self.portfolio: Optional[DataFrame] = None
        self.current_window: Window = inital_window

        # Is this required? Isn't history just all data since self.start_date? (for an expanding window)
        # Indi thinking to himself
        self.history: List[Window] = [inital_window]
        self.today = self.start_date + self.window_length + timedelta(days=1)

        # Days since the start of backtest
        self.days_alive: int = 0
        self.clusterer = Clusterer()
        self.cointegrator = Cointegrator()
        self.filters = Filters(inital_window)

    def trade(self):
        print(f"Today is {self.today.strftime('%Y-%m-%d')}")

        # Using DBScan for now, ensemble later
        cluster_results = self.clusterer.DBScan(self.current_window)

        # Take cluster results and pass into Cointegrator

        # Take cointegrated signals and pass into Filter = filtered signal

        # Take filtered signal

        # roll forward/expand window
        self.__evolve()

    def __evolve(self):
        # Do all the things to push the window forward to next working day

        # Adjust static parameters
        self.today += timedelta(days=1)
        self.window_length += timedelta(days=1)
        self.days_alive += 1

        # Extend window object by one day (expanding)
        self.current_window = self.current_window.evolve()

        # If it's a weekend, evolve again
        if self.today.weekday() >= 5:
            self.__evolve()


if __name__ == '__main__':
    PairTrader(
        start_date=date(2008, 1, 1),
        window_length=timedelta(days=120),
        end_date=None,
    ).trade()
