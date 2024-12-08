import importlib
import os
import tkinter as tk
from tkinter import ttk, messagebox
from backtesting import Backtest
import threading
import pandas as pd
from binance.client import Client
import matplotlib.pyplot as plt
import mplfinance as mpf

def list_strategies():
    strategies = []
    strategy_dir = 'strategies'
    for filename in os.listdir(strategy_dir):
        if filename.endswith('_strategy.py'):
            strategies.append(filename[:-3])
    return strategies

def run_backtest():
    global bt 
    try:
        run_button.config(text="Ładowanie...", state="disabled")
        root.update()

        friendly_name = symbol_var.get()
        if not friendly_name:
            messagebox.showerror("Błąd", "Wybierz instrument")
            reset_button()
            return

        symbol = symbol_mapping.get(friendly_name)

        strategy_name = strategy_var.get()
        if not strategy_name:
            messagebox.showerror("Błąd", "Wybierz strategię")
            reset_button()
            return

        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        if not start_date or not end_date:
            messagebox.showerror("Błąd", "Podaj przedział czasowy (datę początkową i końcową)")
            reset_button()
            return

        try:
            initial_cash = float(initial_cash_entry.get())
            if initial_cash <= 0:
                raise ValueError("Kapitał początkowy musi być większy od zera.")
        except ValueError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowy kapitał początkowy: {e}")
            reset_button()
            return

        module_name = f"strategies.{strategy_name}"
        strategy_module = importlib.import_module(module_name)

        StrategyClass = getattr(strategy_module, 'STRATEGY_CLASS')
        get_data = getattr(strategy_module, 'get_data')

        params = {
            'symbol': symbol,
            'start': start_date,
            'end': end_date
        }

        data = get_data(**params)
        bt = Backtest(data, StrategyClass, cash=initial_cash, commission=0.0015)
        output = bt.run()

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(output))
        result_text.insert(tk.END, f"\n\nSaldo końcowe: {output['Equity Final [$]']:.2f} USD")

        visualize_button.grid(row=8, column=0, columnspan=2, pady=10)
    
    except Exception as e:
        messagebox.showerror("Błąd", f"Coś poszło nie tak: {e}")
    finally:
        reset_button()

def reset_button():
    run_button.config(text="Uruchom Backtest", state="normal")

def start_backtest_thread():
    threading.Thread(target=run_backtest, daemon=True).start()

def visualize_backtest():
    if bt:
        bt.plot()

def show_chart_window():
    chart_window = tk.Toplevel(root)
    chart_window.title("Wyświetl wykres")

    tk.Label(chart_window, text="Wybierz instrument:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    symbol_var_chart = tk.StringVar()
    symbol_combo_chart = ttk.Combobox(chart_window, textvariable=symbol_var_chart, values=list(symbol_mapping.keys()), state='readonly')
    symbol_combo_chart.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(chart_window, text="Data początkowa (np. '2024-01-01'):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    start_date_entry_chart = tk.Entry(chart_window)
    start_date_entry_chart.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(chart_window, text="Data końcowa (np. '2024-12-31'):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    end_date_entry_chart = tk.Entry(chart_window)
    end_date_entry_chart.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(chart_window, text="Okres świecy:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    interval_var = tk.StringVar()
    interval_combo = ttk.Combobox(chart_window, textvariable=interval_var, values=["15m", "1h", "4h", "1d"], state='readonly')
    interval_combo.grid(row=3, column=1, padx=10, pady=5)

    tk.Button(chart_window, text="Wyświetl wykres", command=lambda: plot_chart(symbol_var_chart.get(), start_date_entry_chart.get(), end_date_entry_chart.get(), interval_var.get())).grid(row=4, column=0, columnspan=2, pady=10)

def plot_chart(symbol_name, start, end, interval):
    try:
        if not symbol_name or not start or not end or not interval:
            messagebox.showerror("Błąd", "Wprowadź wszystkie parametry!")
            return

        symbol = symbol_mapping.get(symbol_name)
        if not symbol:
            messagebox.showerror("Błąd", "Nieprawidłowy symbol")
            return

        client = Client()
        frame = pd.DataFrame(client.get_historical_klines(symbol, interval, start, end))
        frame = frame[[0, 1, 2, 3, 4, 5]]
        frame.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        frame['Date'] = pd.to_datetime(frame['Date'], unit='ms')
        frame.set_index('Date', inplace=True)
        frame = frame.astype(float)

        mpf.plot(frame, type='candle', style='charles', 
                 title=f'{symbol_name} - Wykres {interval}',
                 ylabel='Cena (USD)', volume=False)

    except Exception as e:
        messagebox.showerror("Błąd", f"Coś poszło nie tak: {e}")


root = tk.Tk()
root.title("Trading Bot - Backtesting GUI")

chart_button_frame = tk.Frame(root)
chart_button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

chart_button = tk.Button(chart_button_frame, text="Wyświetl wykres", command=show_chart_window)
chart_button.pack()

input_frame = tk.Frame(root)
input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

symbol_label = tk.Label(input_frame, text="Wybierz instrument:")
symbol_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

symbol_mapping = {
    'ETH (Ethereum)': 'ETHUSDT',
    'SOL (Solana)': 'SOLUSDT',
    'DOGE (Dogecoin)': 'DOGEUSDT',
    'SHIB (Shiba Inu)': 'SHIBUSDT',
    'BTC (Bitcoin)': 'BTCUSDT',
    'ADA (Cardano)': 'ADAUSDT',
    'XRP (Ripple)': 'XRPUSDT',
    'DOT (Polkadot)': 'DOTUSDT',
    'LTC (Litecoin)': 'LTCUSDT',
    'BNB (Binance Coin)': 'BNBUSDT',
    'AVAX (Avalanche)': 'AVAXUSDT',
    'MATIC (Polygon)': 'MATICUSDT',
    'ATOM (Cosmos)': 'ATOMUSDT',
    'LINK (Chainlink)': 'LINKUSDT',
    'UNI (Uniswap)': 'UNIUSDT',
    'XLM (Stellar)': 'XLMUSDT',
    'TRX (Tron)': 'TRXUSDT',
    'NEAR (NEAR Protocol)': 'NEARUSDT',
    'ALGO (Algorand)': 'ALGOUSDT'
}

friendly_symbols = list(symbol_mapping.keys())
symbol_var = tk.StringVar()
symbol_combo = ttk.Combobox(input_frame, textvariable=symbol_var, values=friendly_symbols, state='readonly')
symbol_combo.grid(row=0, column=1, padx=5, pady=5)

strategy_label = tk.Label(input_frame, text="Wybierz strategię:")
strategy_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

strategies = list_strategies()
strategy_var = tk.StringVar()
strategy_combo = ttk.Combobox(input_frame, textvariable=strategy_var, values=strategies, state='readonly')
strategy_combo.grid(row=1, column=1, padx=5, pady=5)

start_date_label = tk.Label(input_frame, text="Data początkowa (np. '2024-01-01'):")
start_date_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

start_date_entry = tk.Entry(input_frame)
start_date_entry.grid(row=2, column=1, padx=5, pady=5)

end_date_label = tk.Label(input_frame, text="Data końcowa (np. '2024-12-31'):")
end_date_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

end_date_entry = tk.Entry(input_frame)
end_date_entry.grid(row=3, column=1, padx=5, pady=5)

initial_cash_label = tk.Label(input_frame, text="Kapitał początkowy (USD):")
initial_cash_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

initial_cash_entry = tk.Entry(input_frame)
initial_cash_entry.insert(0, "100000")
initial_cash_entry.grid(row=4, column=1, padx=5, pady=5)

run_button = tk.Button(root, text="Uruchom Backtest", command=start_backtest_thread)
run_button.grid(row=2, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="Wynik backtestu:", font=("Helvetica", 12, "bold"))
result_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")

result_text = tk.Text(root, wrap="word", height=15, width=80)
result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

visualize_button = tk.Button(root, text="Pobierz wizualizację backtestu", command=visualize_backtest)
visualize_button.grid(row=5, column=0, columnspan=2, pady=10)
visualize_button.grid_remove()

root.mainloop()