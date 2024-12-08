import importlib
from backtesting import Backtest
import os
import sys

def list_strategies():
    strategies = []
    strategy_dir = 'strategies'
    for filename in os.listdir(strategy_dir):
        if filename.endswith('_strategy.py'):
            strategies.append(filename[:-3])
    return strategies

def run_backtest(strategy_name, symbol, start_date):
    module_name = f"strategies.{strategy_name}"
    strategy_module = importlib.import_module(module_name)

    StrategyClass = getattr(strategy_module, 'STRATEGY_CLASS')
    get_data = getattr(strategy_module, 'get_data')

    params = {'symbol': symbol, 'start': start_date}
    data = get_data(**params)
    bt = Backtest(data, StrategyClass, cash=100000, commission=0.0015)
    output = bt.run()
    print(output)
    bt.plot()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        import gui
    else:
        strategies = list_strategies()
        print("Dostępne strategie:")
        for idx, strategy in enumerate(strategies, 1):
            print(f"{idx}. {strategy}")

        choice = int(input("Wybierz strategię wpisując odpowiadający jej numer: "))
        strategy_name = strategies[choice - 1]

        symbol = input("Podaj symbol (np. 'ETHUSDT'): ")
        start_date = input("Podaj datę początkową (np. '2024-01-01'): ")

        run_backtest(strategy_name, symbol, start_date)

if __name__ == "__main__":
    main()
