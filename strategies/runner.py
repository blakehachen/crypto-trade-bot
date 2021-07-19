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

class Runner(Strategy):
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
            data={'uuid': str(uuid.uuid4().hex),'exchange':self.exchange.name.lower(), 'periodStart':datetime.now(), 'periodEnd':'live_trade', 'candleSize': 60,
            'currency': self.exchange.currency, 'asset':self.exchange.asset}
        )

    def run(self):
        self.get_portfolio()
        self.exchange.get_asset_balance(self.exchange.currency)
        self.exchange.get_asset_balance(self.exchange.asset)
        
        current_price = self.exchange.symbol_ticker()
        price_data = self.exchange.historical_symbol_ticker_candle(str(datetime.now() - timedelta(minutes=30)))
        
        closes = []
        highs = []
        lows = []
        for price in price_data:
            closes.append(float(price.close))
            highs.append(float(price.highest))
            lows.append(float(price.lowest))

        np_highs = np.array(highs)
        np_lows = np.array(lows)
        np_closes = np.array(closes)
        #print(np_closes)
        adx = ta.ADX(np_highs, np_lows, np_closes, timeperiod=14)
        #print(adx)
        fastk, fastd = ta.STOCHRSI(np_closes, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        ShortEMA = ta.EMA(np_closes, 9)
        #print(ShortEMA)
        LongEMA = ta.EMA(np_closes, 18)
        #print(LongEMA)
        MACD = ShortEMA - LongEMA
        #print(MACD)
        signal = ta.EMA(MACD, 5)

        upperband, middleband, lowerband = ta.BBANDS(np_closes, timeperiod=18, nbdevup=2, nbdevdn=2, matype=0)
        upperband_crossed = np.where((np_closes > upperband), 1, 0)
        lowerband_crossed = np.where((np_closes < lowerband), 1, 0)

        last_upperband_crossed = upperband_crossed[-1]
        last_lowerband_crossed = lowerband_crossed[-1]
        last_macd = MACD[-1]
        last_signal = signal[-1]
        last_fastk = fastk[-1]
        last_fastd = fastd[-1]
        last_adx = adx[-1]
        
        should_buy = 0
        should_sell = 0

        
        
        if last_macd > last_signal:
            should_buy += 1

        if last_lowerband_crossed:
            should_buy += 1

        if last_macd < last_signal:
            should_sell += 1

        if last_upperband_crossed:
            should_sell += 1

        if last_fastd > 90 and last_fastk > 90:
            should_buy += 1

        if last_fastd <= 20 and last_fastk <= 20:
            should_sell += 1
        
        average = round(mean(np_closes), 4)
        #average = round(((float(price.open) + float(price.lowest) + float(price.close) + float(price.highest))/4), 4)
        if should_buy > 0:
            print(f'[ BUY ] {str(should_buy)}')
        if should_sell > 0:
            print(f'[ SELL ] {str(should_sell)}')
        print(f"For a good buy.\n" +
              f"last_macd ({str(last_macd)}) > last_signal({str(last_signal)})\nlast_lowerband_crossed: {str(last_lowerband_crossed)}\nlast_fastd({str(last_fastd)}) > 90 and last_fastk({str(last_fastk)}) > 90\nlowest price({price.lowest}) < current price({str(current_price.current)}) < avaerage price({str(average)})\n\n" +
              f"For a good sell.\n" +
              f"last_macd({str(last_macd)}) < last_signal({str(last_signal)})\n last_upperband_crossed: {str(last_upperband_crossed)}\n last_fastd({str(last_fastd)} <= 20 and last_fastk({str(last_fastk)}) <= 20 )\nhighest price({price.highest}) > current price({str(current_price.current)}) > avaerage price({str(average)})\n\n")
        print(f'LAST ADX INDICATOR: {str(last_adx)}\n' +
               'If ADX (0-25): Trend is absent or weak\n' +
               'If ADX (25-50): Trend is strong\n'+
               'If ADX (50-75): Trend is very strong\n' +
               'If ADX (75-100): Trend is extremely strong\n')
        
        print('Buy Points: ' + str(should_buy))
        print('Sell Points: ' + str(should_sell) + '\n')
        
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string)
        
        #HLC Average = (High + Low + Close) / 3
        
        if should_buy == 2 and float(price.lowest) <= float(current_price.current) < float(average) and should_sell == 0 and datetime.now() > (datetime.fromtimestamp(int(self.get_recent_order_time())/1000) + timedelta(minutes=3)) and last_adx >= 30:
            print(f'[LOW BUY] : {price.close}')
            if float(self.exchange.get_asset_balance(self.exchange.asset))/float(current_price.current) > 20:
                newOrder = Order()
                newOrder.quantity = int(round((0.20 * float(float(self.exchange.get_asset_balance(self.exchange.asset))/float(current_price.current))),2))
                newOrder.price = float(current_price.current)
                newOrder.side = newOrder.BUY
                newOrder.type = newOrder.TYPE_LIMIT
                newOrder.currency = self.exchange.currency
                newOrder.asset = self.exchange.asset
                newOrder.symbol = self.exchange.get_symbol()
                print(newOrder.quantity)
                self.order(newOrder)
        elif should_buy == 2 and float(price.lowest) <= float(current_price.current) < average and datetime.now() > (datetime.fromtimestamp(int(self.get_recent_order_time())/1000) + timedelta(minutes=3)) and last_adx >= 30:
            print(f'[MEDIUM BUY] : {price.close}')
            if float(self.exchange.get_asset_balance(self.exchange.asset))/float(current_price.current):
                newOrder = Order()
                newOrder.quantity = int(round((0.33 * float(float(self.exchange.get_asset_balance(self.exchange.asset))/float(current_price.current))),2))
                newOrder.price = float(current_price.current)
                newOrder.side = newOrder.BUY
                newOrder.type = newOrder.TYPE_LIMIT
                newOrder.currency = self.exchange.currency
                newOrder.asset = self.exchange.asset
                newOrder.symbol = self.exchange.get_symbol()
                print(newOrder.quantity)
                self.order(newOrder)
        if should_sell == 2 and float(price.highest) >= float(current_price.current) > float(average) and should_buy == 0 and datetime.now() > (datetime.fromtimestamp(int(self.get_recent_order_time())/1000) + timedelta(minutes=3)) and last_adx >= 30:
            print(f'[MEDIUM SELL] : {price.close}')
            if float(self.exchange.get_asset_balance(self.exchange.currency)) > 75:
                newOrder = Order()
                newOrder.quantity = int(round((0.33 * float(self.exchange.get_asset_balance(self.exchange.currency))),2))
                newOrder.price = float(current_price.current)
                newOrder.side = newOrder.SELL
                newOrder.type = newOrder.TYPE_LIMIT
                newOrder.currency = self.exchange.currency
                newOrder.asset = self.exchange.asset
                newOrder.symbol = self.exchange.get_symbol()
                print(newOrder.quantity)
                self.order(newOrder)
        elif should_sell == 2 and float(price.highest) >= float(current_price.current) > float(average) and datetime.now() > (datetime.fromtimestamp(int(self.get_recent_order_time())/1000) + timedelta(minutes=3)) and last_adx >= 30:
            print(f'[LOW SELL] : {price.close}')
            if float(self.exchange.get_asset_balance(self.exchange.currency)) > 75:
                newOrder = Order()
                newOrder.quantity = int(round((0.10 * float(self.exchange.get_asset_balance(self.exchange.currency))),2))
                newOrder.price = float(current_price.current)
                newOrder.side = newOrder.SELL
                newOrder.type = newOrder.TYPE_LIMIT
                newOrder.currency = self.exchange.currency
                newOrder.asset = self.exchange.asset
                newOrder.symbol = self.exchange.get_symbol()
                print(newOrder.quantity)
                self.order(newOrder)
        
        if should_sell == 3 and float(price.highest) >= float(current_price.current) > float(average) and datetime.now() > (datetime.fromtimestamp(int(self.get_recent_order_time())/1000) + timedelta(minutes=3)) and last_adx >= 40:
            print(f'[STRONG SELL] : {price.close}')
            if float(self.exchange.get_asset_balance(self.exchange.currency)) > 75:
                newOrder = Order()
                newOrder.quantity = int(round((0.50 * float(self.exchange.get_asset_balance(self.exchange.currency))),2))
                newOrder.price = float(current_price.current)
                newOrder.side = newOrder.SELL
                newOrder.type = newOrder.TYPE_LIMIT
                newOrder.currency = self.exchange.currency
                newOrder.asset = self.exchange.asset
                newOrder.symbol = self.exchange.get_symbol()
                print(newOrder.quantity)
                self.order(newOrder)

        if should_buy == 3 and float(price.lowest) <= float(current_price.current) < float(average) and datetime.now() > (datetime.fromtimestamp(int(self.get_recent_order_time())/1000) + timedelta(minutes=3)) and last_adx >= 40:
            print(f'[STRONG BUY] : {price.close}')
            if float(self.exchange.get_asset_balance(self.exchange.asset))/float(current_price.current):
                newOrder = Order()
                newOrder.quantity = int(round((1.0 * float((float(self.exchange.get_asset_balance(self.exchange.asset)))/float(current_price.current)) - 2),2))
                newOrder.price = float(current_price.current)
                newOrder.side = newOrder.BUY
                newOrder.type = newOrder.TYPE_LIMIT
                newOrder.currency = self.exchange.currency
                newOrder.asset = self.exchange.asset
                newOrder.symbol = self.exchange.get_symbol()
                print(newOrder.quantity)
                self.order(newOrder)
            pass

        
        print('*******************************')
        print('Exchange: ', self.exchange.name)
        print('Pair: ', self.exchange.compute_symbol_pair())
        print('Available: ',  self.exchange.get_asset_balance(self.exchange.currency) + ' ' +self.exchange.currency)
        print('Available: ', self.exchange.get_asset_balance(self.exchange.asset) + ' ' + self.exchange.asset)
        print('Price: ', current_price.current)
        #print(f'{self.exchange.historical_symbol_ticker_candle(str(datetime.now() - timedelta(days=14)), str(datetime.now()))}')
        #self.buy()
        print(self.dataset)
        print(self.price)
        response = self.price.create(data={"dataset": self.dataset.uuid})
        print(response)
        print('\n\n')