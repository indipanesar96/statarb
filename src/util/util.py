


from src.DataRepository import Universes
from src.util.Tickers import EtfTickers, SnpTickers



def get_universe_from_ticker(t):
    if isinstance(t, SnpTickers):
        return Universes.SNP
    else:
        return Universes.ETFs


if __name__ == '__main__':
    print(get_universe_from_ticker(SnpTickers.A))
    print(get_universe_from_ticker(EtfTickers.ACES))