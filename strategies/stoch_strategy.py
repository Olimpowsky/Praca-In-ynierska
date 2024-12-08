import pandas as pd
import ta
from backtesting import Strategy
from backtesting.lib import crossover
from binance.client import Client
import ta.momentum

def get_data(symbol, start, end):
    client = Client()
    frame = pd.DataFrame(client.get_historical_klines(symbol, '1d', start, end))
    frame = frame[[0,1,2,3,4]]
    frame.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    frame.Date = pd.to_datetime(frame.Date, unit='ms')
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    return frame

class StochasticOscillatorStrategy(Strategy):
    def init(self):
        high = pd.Series(self.data.High, index=self.data.index)
        low = pd.Series(self.data.Low, index=self.data.index)
        close = pd.Series(self.data.Close, index=self.data.index)

        stoch = ta.momentum.StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3)
        self.stoch_k = self.I(lambda: stoch.stoch())
        self.stoch_d = self.I(lambda: stoch.stoch_signal())

    def next(self):
        stoch_k = self.stoch_k[-1]
        price = self.data.Close[-1]

        if crossover(self.stoch_k, self.stoch_d) and stoch_k < 20:
            if not self.position.is_long:
                if self.position.is_short:
                    self.position.close()
                sl = price * 0.97
                self.buy(sl=sl)
        elif crossover(self.stoch_d, self.stoch_k) and stoch_k > 80:
            if not self.position.is_short:
                if self.position.is_long:
                    self.position.close()
                sl = price * 1.03
                self.sell(sl=sl)
STRATEGY_CLASS = StochasticOscillatorStrategy

def get_parameters():
    symbol = input("Podaj symbol (np. 'ETHUSDT'): ")
    start_date = input("Podaj datę początkową (np. '2024-01-01'): ")
    return {'symbol': symbol, 'start': start_date}
