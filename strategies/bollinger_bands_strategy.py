import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover
from binance.client import Client

def get_data(symbol, start, end):
    client = Client()
    frame = pd.DataFrame(client.get_historical_klines(symbol, '4h', start, end))
    frame = frame[[0, 1, 2, 3, 4]]
    frame.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    frame['Date'] = pd.to_datetime(frame['Date'], unit='ms')
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    return frame

class ClassicBollingerBandsStrategy(Strategy):
    def init(self):
        close = self.data.Close

        self.middle_band = self.I(lambda x: pd.Series(x).rolling(window=20).mean(), close)
        self.std_dev = self.I(lambda x: pd.Series(x).rolling(window=20).std(), close)

        self.upper_band = self.I(lambda: self.middle_band + 2 * self.std_dev)
        self.lower_band = self.I(lambda: self.middle_band - 2 * self.std_dev)

    def next(self):
        price = self.data.Close[-1]

        if price < self.lower_band[-1] and not self.position:
            sl = price * 0.97 
            tp = price * 1.05 
            self.buy(sl=sl, tp=tp)

        elif price > self.upper_band[-1] and not self.position:
            sl = price * 1.03 
            tp = price * 0.95
            self.sell(sl=sl, tp=tp)

STRATEGY_CLASS = ClassicBollingerBandsStrategy

def get_parameters():
    symbol = input("Podaj symbol (np. 'ETHUSDT'): ")
    start_date = input("Podaj datę początkową (np. '2021-01-01'): ")
    end_date = input("Podaj datę końcową (np. '2022-01-01'): ")
    return {'symbol': symbol, 'start': start_date, 'end': end_date}
