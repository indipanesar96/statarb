from src.TickerData import TickerData
from datetime import date
from src.Plotter import Plotter

start_date: date = date(2016, 1, 1)
end_date: date = date(2019, 1, 1)

spy: TickerData = TickerData('SPY', start_date, end_date)  # https://www.etf.com/SPY
vti: TickerData = TickerData('VTI', start_date, end_date)  # https://www.etf.com/VTI#overview
ubio: TickerData = TickerData('UBIO', start_date, end_date)  # https://www.etf.com/UBIO
soxl: TickerData = TickerData('SOXL', start_date, end_date)  # https://www.etf.com/UBIO

Plotter.plot((vti, spy, ubio, soxl))
