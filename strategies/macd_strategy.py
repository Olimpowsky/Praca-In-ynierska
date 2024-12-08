import pandas as pd
import ta
from backtesting import Strategy
from backtesting.lib import crossover
import ta.trend
from binance.client import Client

def get_data(symbol, start, end):
    client = Client()
    frame = pd.DataFrame(client.get_historical_klines(symbol, '4h', start, end))
    frame = frame[[0,1,2,3,4]]
    frame.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    frame.Date = pd.to_datetime(frame.Date, unit='ms')
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    return frame

class MACDStrategy(Strategy):
    def init(self):
        close = self.data.Close
        self.macd = self.I(ta.trend.macd, pd.Series(close))
        self.macd_signal = self.I(ta.trend.macd_signal, pd.Series(close))
        self.ema_100 = self.I(ta.trend.ema_indicator, pd.Series(close), window=100)

    def next(self):
        price = self.data.Close
        if crossover(self.macd, self.macd_signal) and price > self.ema_100:
            sl = price * 0.97
            tp = price * 1.045
            self.buy(sl=sl, tp=tp)
STRATEGY_CLASS = MACDStrategy

def get_parameters():
    symbol = input("Podaj symbol (np., 'ETHUSDT'): ")
    start_date = input("Podaj datę początkową (np., '2024-01-01'): ")
    return {'symbol': symbol, 'start': start_date}



