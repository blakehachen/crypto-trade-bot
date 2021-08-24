from binance.enums import SIDE_BUY
from models.model import AbstractModel
from decouple import config

class Position(AbstractModel):

    resource_name = 'positions'

    dataset: str = ''
    symbol: str = ''
    currency: str = ''
    asset: str = ''
    price: float = 0
    side: str = ''
    quantity: int = 0
    current: float = 0
    stop: str = ''
    stopPrice: float = 0
    stopPriceType: str = ''
    tests: bool = False
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)