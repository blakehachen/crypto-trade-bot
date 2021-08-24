from datetime import datetime
from math import floor
from models.exchange import Exchange
from models.currency import Currency
import json
from binance.client import Client
from binance.enums import *
from binance.streams import BinanceSocketManager

from api import utils
from .exchange import Exchange
from models.order import Order
from models.price import Price

class Binance(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)

        self.client = Client(self.apiKey, self.apiSecret, tld='us')
        self.name = self.__class__.__name__

    def get_client(self):
        return self.client

    def get_symbol(self):
        return self.currency + self.asset

    def symbol_ticker(self):
        response = self.client.get_symbol_ticker(symbol=self.get_symbol())
        print(response)

        return Price(pair=self.get_symbol(), currency=self.currency.lower(), asset=self.asset.lower(), exchange=self.name.lower(),
                     current=response['price'], openAt=utils.format_date(datetime.now()))

    def symbol_ticker_candle(self, interval=Client.KLINE_INTERVAL_1MINUTE):
        return self.client.get_klines(symbol=self.get_symbol(), interval=interval)

    def historical_symbol_ticker_candle(self, start: datetime, end=None, interval=Client.KLINE_INTERVAL_1MINUTE):
        #if isinstance(interval, int):
        #    interval = str(floor(interval/60)) + 'm'
        start = str(start)
        output = []
        for candle in self.client.get_historical_klines_generator(self.get_symbol(), interval, start, end):
            #print(f'P{candle}')
            output.append(
                Price(pair=self.compute_symbol_pair(), currency=self.currency.lower(), asset=self.asset.lower(), 
                        exchange=self.name.lower(), lowest = candle[3], highest=candle[2], volume=candle[7], open=candle[2], close=candle[4], openAt=utils.format_date(datetime.fromtimestamp(int(candle[0])/1000)))
            )
        #print(json.dumps(output, indent=2))
        return output

    def get_asset_balance(self, currency):
        response = self.client.get_asset_balance(currency)
        return response['free']

    def get_contract_balance(self, currency):
        response = self.client.get_asset_balance(currency)
        return response['free']

    def order(self, order: Order):
        return self.client.create_order(
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=order.quantity,
            price=order.price
        )

    def test_order(self, order: Order):
        return self.client.create_test_order(
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=order.quantity,
            price=order.price
        )

    def check_order(self, orderId):
        return self.client.get_order(
            symbol=self.get_symbol(),
            orderId=orderId
        )
    def get_recent_orders(self):
        return self.client.get_all_orders(
            symbol=self.get_symbol(),
            limit=10
        )

    def get_recent_orders_time(self):
        return self.get_recent_orders()[-1]['time']


    def cancel_order(self, orderId):
        return self.client.cancel_order(
            symbol=self.get_symbol(),
            orderId=orderId
        )

    def get_socket_manager(self):
        return BinanceSocketManager(self.client)

    def start_symbol_ticker_socket(self, symbol: str):
        self.socketManager = self.get_socket_manager()
        self.socket = self.socketManager.symbol_ticker_socket(
            symbol=self.get_symbol(),
        )
        self.start_socket()

    def websocket_event_handler(self, msg):
        if msg['e'] == 'error':
            print(msg)
            self.close_socket()
        else:
            self.strategy.set_price(
                Price(pair=self.compute_symbol_pair(), currency=self.currency, asset=self.asset, exchange=self.name,
                      current=msg['b'], lowest=msg['l'], highest=msg['h'])
            )
            self.strategy.run()