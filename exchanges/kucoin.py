from datetime import datetime
from math import floor
from typing import Sized
from models.exchange import Exchange
from models.currency import Currency
import json

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.client import Trade
from kucoin_futures.client import Market
from kucoin_futures.client import User

from api import utils
from .exchange import Exchange
from models.order import Order
from models.price import Price

from decouple import config

class Kucoin(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)

        self.userClient = User(key=self.apiKey, secret=self.apiSecret, passphrase=config("KUCOIN_PASSPHRASE"))
        self.marketClient = Market(url='https://api-futures.kucoin.com')
        self.tradeClient = Trade(key=self.apiKey, secret=self.apiSecret, passphrase=config("KUCOIN_PASSPHRASE"), is_sandbox=False, url='')
        self.name = self.__class__.__name__
    
    def get_client(self):
        return self.marketClient

    def get_symbol(self):
        return self.currency + self.asset
    
    def symbol_ticker(self):
        response = self.marketClient.get_current_mark_price(self.get_symbol())
        print(response)
        return Price(pair=self.get_symbol(), currency=self.currency.lower(), asset=self.asset.lower(), exchange=self.name.lower(),
                     current=response['value'], openAt=utils.format_date(datetime.now()))

    def symbol_ticker_candle(self, interval=1):
        return self.marketClient.get_kline_data(self.get_symbol(), interval)

    def historical_symbol_ticker_candle(self, start: datetime, end=None, interval=1):
        #convert datetime to ms
        start_n = int(start.timestamp() * 1000)
        if end is not None:
            end_n = int(end.timestamp() * 1000)
        else:
            end_n = None

        output = []
        for candle in self.marketClient.get_kline_data(self.get_symbol(), interval, start_n, end_n):
            output.append(
                Price(pair=self.compute_symbol_pair(), currency=self.currency.lower(), asset=self.asset.lower(), 
                        exchange=self.name.lower(), lowest = candle[3], highest=candle[2], volume=candle[5], open=candle[1], close=candle[4], openAt=utils.format_date(datetime.fromtimestamp(int(candle[0])/1000)))
            )
        return output
    
    def get_asset_balance(self, currency):
        response = self.userClient.get_account_overview(currency='USDT')
        return response['availableBalance']
    
    def get_contract_balance(self, currency):
        return self.tradeClient.get_position_details(self.get_symbol())['posInit']
        

    def order(self, order: Order):
        return self.tradeClient.create_market_order(
            symbol=order.symbol,
            side=order.side,
            lever=order.leverage,
            price=order.price,
            size=order.quantity,
            timeInForce='GTC',
        )
    
    def test_order(self, order: Order):
        pass

    def check_order(self, orderId):
        return self.tradeClient.get_order_details(
            orderId
        )
    def get_recent_orders(self):
        return self.tradeClient.get_order_list(
            symbol=self.get_symbol(),
            pageSize=10
        )
    def get_recent_orders_time(self):
        orders = self.get_recent_orders()
        for item in orders['items']:
            timestamp = int(item['createdAt']) / 1000
        return timestamp


    def cancel_order(self, orderId):
        return self.tradeClient.cancel_order(
            orderId
        )
    
    def get_socket_manager(self):
        client = WsToken(key=config("KUCOIN_API_KEY"), secret=config("KUCOIN_API_SECRET"), passphrase=config("KUCOIN_PASSPHRASE"), is_sandbox=False, url='')
        return KucoinFuturesWsClient.create(60, client, 'msg')

    def start_symbol_ticker_socket(self, symbol: str):
        self.socketManager = self.get_socket_manager()
        self.socketManager.subscribe('/contractMarket/level2:'+ self.get_symbol())
        

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

    def trade_profit_loss(self, close_price):
        position_ticker = self.get_symbol()
        entry_price = float(position_ticker['avgEntryPrice'])
        realisedPnL = float(position_ticker['realisedPnl'])
        total_PnL = (close_price - entry_price) + realisedPnL
        return total_PnL

    def check_position(self):
        position_ticker = self.get_symbol()


