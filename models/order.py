from binance.enums import SIDE_BUY
from models.model import AbstractModel
from decouple import config

class Order(AbstractModel):

    BUY = 'BUY'
    SELL = 'SELL'
    TYPE_LIMIT = 'LIMIT'
    TYPE_MARKET = 'MARKET'
    TYPE_STOP_LOSS = 'STOP_LOSS'
    TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'

    resource_name = 'orders'

    type: str = TYPE_MARKET
    leverage: int = int(config("LEVERAGE"))
    symbol: str = ''
    currency: str = ''
    asset: str = ''
    price: float = 0
    side: str = ''
    quantity: int = 0
    lot_unit: float = float(config("LOT_UNIT"))
    stop: str = ''
    stopPrice: float = 0
    stopPriceType: str = ''
    tests: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)