
import importlib
import signal

import sys
import threading
from decouple import config

from testing.backtest import Backtest
from testing.importer import Importer

exchange_name = config('EXCHANGE')
mode: str = config('MODE')
strategy: str = config('STRATEGY')
trading_mode: str = config('TRADING_MODE')
interval: int = int(config('CANDLE_INTERVAL'))
currency: str = config('CURRENCY')
asset: str = config('ASSET')

if trading_mode == 'real':
    print('trading mode initiated..')
else:
    print('Testing')

if len(sys.argv) > 1:
    currencies = sys.argv[1].split('_')
    if len(currencies) > 1:
        currency = currencies[0]
        asset = currencies[1]

print("Establishing connection to {} exchange".format(exchange_name))
exchangeModule = importlib.import_module("exchanges."+exchange_name, package=None)
exchangeClass = getattr(exchangeModule, exchange_name[0].upper() + exchange_name[1:])
exchange = exchangeClass(config("API_KEY"), config("API_SECRET"))
exchange.set_currency(currency)
exchange.set_asset(asset)
print(currency+"_"+asset)

strategyModule = importlib.import_module('strategies.' + strategy, package=None)
strategyClass = getattr(strategyModule, strategy[0].upper() + strategy[1:])
exchange.set_strategy(strategyClass(exchange, interval))

print("Currently trading in {} mode, watching {}".format(mode, exchange.get_symbol()))
if mode == 'trade':
    exchange.strategy.start()

elif mode == 'live':
    exchange.start_symbol_ticker_socket(exchange.get_symbol())

elif mode == 'backtest':
    period_start = config("PERIOD_START")
    period_end = config("PERIOD_END")

    print(f"Backtest from {period_start} to {period_end} with {interval} seconds candlesticks")

    Backtest(exchange, period_start, period_end, interval)
elif mode == 'import':
    period_start = config('PERIOD_START')
    period_end = config('PERIOD_END')

    print(
        "Import mode on {} symbol for period from {} to {} with {} seconds candlesticks.".format(
            exchange.get_symbol(),
            period_start,
            period_end,
            interval
        )
    )
    importer = Importer(exchange, period_start, period_end, interval)
    importer.process()
else:
    print('mode not supported check env file')

def signal_handler(signal, frame):
    if(exchange.socket):
        print('Closing WebSocket connection....')
        exchange.close_socket()
        sys.exit(0)
    else:
        print('stopping strategy....')
        exchange.strategy.stop()
        sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
forever = threading.Event()
forever.wait()
exchange.strategy.stop()
sys.exit(0)


