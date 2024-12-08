import pandas as pd
import ta
from backtesting import Strategy
from binance.client import Client
from backtesting.lib import crossover
import ta.momentum
import ta.trend

def get_data(symbol, start, end):
    client = Client()
    frame = pd.DataFrame(client.get_historical_klines(symbol, '4h', start, end))
    frame = frame[[0,1,2,3,4]]
    frame.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    frame['Date'] = pd.to_datetime(frame['Date'], unit='ms')
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    return frame

class RSIStrategy(Strategy):
    def init(self):
        close = self.data.df['Close']

        rsi_indicator = ta.momentum.RSIIndicator(close=close, window=14)
        self.rsi = self.I(rsi_indicator.rsi)
        self.ema_100 = self.I(ta.trend.ema_indicator, pd.Series(close), window=200)


    def next(self):
        price = self.data.Close[-1]
        if crossover(self.rsi, 30) and price > self.ema_100:
            if not self.position.is_long:
                if self.position.is_short:
                    self.position.close() 
                self.buy()
        elif crossover(70, self.rsi) and price < self.ema_100:
            if not self.position.is_short:
                if self.position.is_long:
                    self.position.close()
                self.sell()

STRATEGY_CLASS = RSIStrategy

def get_parameters():
    symbol = input("Podaj symbol (np., 'ETHUSDT'): ")
    start_date = input("Podaj datę początkową (np., '2024-01-01'): ")
    return {'symbol': symbol, 'start': start_date}
