import numpy as np
import requests
from const import ORDERBOOK_DEPTH

BINANCE_API_V3 = 'https://api.binance.com/api/v3/'
SYMBOLS_URL = BINANCE_API_V3 + 'exchangeInfo'
TICKERS_URL = BINANCE_API_V3 + 'ticker/24hr'
ORDERBOOK_URL = BINANCE_API_V3 + 'depth'
QUOTE_ASSETS = ['AUD', 'BIDR', 'BKRW', 'BNB', 'BRL', 'BTC', 'BUSD', 'DAI', 'ETH', 'EUR', 'GBP',
 'IDRT', 'NGN', 'PAX', 'RUB', 'TRX', 'TRY', 'TUSD', 'UAH', 'USDC', 'USDS', 'USDT',
 'XRP', 'ZAR']

def get_quote_assets():
    response = requests.get(SYMBOLS_URL).json()
    raw_symbols = response['symbols']
    quote_assets = np.unique(np.array(list(map(lambda x: x['quoteAsset'], raw_symbols))))
    return quote_assets

def split_symbol(symbol):
    if symbol[-3:] in QUOTE_ASSETS:
        return symbol[:-3], symbol[-3:]
    return symbol[:-4], symbol[-4:]

def fetch_tickers():
    response = requests.get(TICKERS_URL).json()
    tickers = list(map(lambda x: [split_symbol(x['symbol']), float(x['askPrice']), float(x['bidPrice'])], response))
    return tickers
    
def fetch_orderbook(symbol):
    orderbook = requests.get(ORDERBOOK_URL, {'symbol': symbol, 'limit' : ORDERBOOK_DEPTH}).json()
    return orderbook
