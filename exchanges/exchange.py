import datetime
from api import utils
from abc import ABC, abstractmethod
from twisted.internet import reactor
from strategies.strategy import Strategy
from models.order import Order

class Exchange(ABC):
    currency: str
    asset: str
    strategy: Strategy

    def __init__(self, key: str, secret: str):
        self.apiKey = key
        self.apiSecret = secret
        self.name = None
        self.client = None
        self.socketManager = None
        self.socket = None
        self.currency = ''
        self.asset = ''
        self.strategy = None
        self.marketClient = None
        self.tradeClient = None

    def set_currency(self, symbol: str):
        self.currency = symbol

    def set_asset(self, symbol: str):
        self.asset = symbol
    
    def set_strategy(self, strategy: Strategy):
        self.strategy = strategy

    def compute_symbol_pair(self):
        return utils.format_pair(self.currency, self.asset)

    @abstractmethod
    def get_symbol(self):
        return self.compute_symbol_pair(self)

    @abstractmethod
    def symbol_ticker(self):
        pass
    
    @abstractmethod
    def symbol_ticker_candle(self, interval):
        pass

    @abstractmethod
    def historical_symbol_ticker_candle(self, start: datetime, end=None, interval=60):
        pass

    @abstractmethod
    def get_asset_balance(self, currency):
        pass
    
    @abstractmethod
    def get_contract_balance(self, currency):
        pass

    @abstractmethod
    def order(self, order: Order):
        pass
    
    @abstractmethod
    def test_order(self, order: Order):
        pass

    @abstractmethod
    def check_order(self, orderId):
        pass
    
    @abstractmethod
    def get_recent_orders(self):
        pass
    @abstractmethod
    def get_recent_orders_time(self):
        pass

    @abstractmethod
    def cancel_order(self, orderId):
        pass

    @abstractmethod
    def get_socket_manager(self, purchase):
        pass
    
    @abstractmethod
    def websocket_event_handler(self, msg):
        pass

    def start_socket(self):
        print('Establishing Connection to WebSocket..')
        self.socketManager.start()

    def close_socket(self):
        #self.socketManager.stop_socket(self.socket)
        #self.socketManager.close()
        reactor.stop()

    @abstractmethod
    def start_symbol_ticker_socket(self, symbol: str):
        pass


    



