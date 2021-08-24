from datetime import date, datetime, timedelta

from numpy.core.fromnumeric import mean
from models.order import Order
import uuid
import talib as ta
import numpy as np
from api import utils
from exchanges.exchange import Exchange
from models.dataset import Dataset
from strategies.strategy import Strategy

class Patterns(Strategy):
    def __init__(self, exchange: Exchange, timeout=60, *args, **kwargs):
        super().__init__(exchange, timeout, *args, **kwargs)

        self.buy_price = 0
        self.sell_price = 0
        self.stop_loss = 0
        self.market_delta = 0

        self.advised = False
        self.waiting_order = False
        self.fulfilled_orders = []
        self.last_price = 0
        
        self.dataset = Dataset().create(
            data={'uuid': str(uuid.uuid4().hex), 'pair':self.exchange.compute_symbol_pair(),'exchange':self.exchange.name.lower(), 'periodStart':datetime.now(), 'periodEnd':'live_trade', 'candleSize': 60,
            'currency': self.exchange.currency, 'asset':self.exchange.asset}
        )
    
    def run(self):
        print('working')

