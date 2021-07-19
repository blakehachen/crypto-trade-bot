import sys
from datetime import datetime

from exchanges.exchange import Exchange
from models.dataset import Dataset
from models.price import Price

class Backtest:
    def __init__(self, exchange: Exchange, period_start: datetime, period_end=None, interval=60):
        self.launchedAt = datetime.now()

        dataset = Dataset().get({
                                "pair": exchange.compute_symbol_pair(),
                                "exchange": exchange.name.lower(),
                                 "currency": exchange.currency.lower(),
                                 "asset": exchange.asset.lower(),
                                 "periodStart": period_start, "periodEnd": period_end, "candleSize": interval})

        if dataset and len(dataset) > 0:
            print(dataset)
            print(dataset[0])
            print("Dataset found: " + str(dataset[0]['uuid']))
            price = Price()
            for item in price.query('get', {"dataset": dataset[0]['uuid']}):
                price.populate(item)
                exchange.strategy.set_price(price)
                exchange.strategy.run()
        else:
            print("Dataset not found, external API call to " + exchange.name)
            for price in exchange.historical_symbol_ticker_candle(period_start, period_end, interval):
                exchange.strategy.set_price(price)
                exchange.strategy.run()

        execution_time = datetime.now() - self.launchedAt
        print('Execution time: ' + str(execution_time.total_seconds()) + ' seconds')
        sys.exit(0)
