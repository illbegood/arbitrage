import numpy as np
import requests
from const import symbols_url, tickers_url, orderbook_url, orderbook_depth, quote_assets

def get_quote_assets():
    response = requests.get(symbols_url).json()
    raw_symbols = response['symbols']
    quote_assets = np.unique(np.array(list(map(lambda x: x['quoteAsset'], raw_symbols))))
    return quote_assets

def split_symbol(symbol):
    if symbol[-3:] in quote_assets:
        return symbol[:-3], symbol[-3:]
    return symbol[:-4], symbol[-4:]

def fetch_tickers():
    response = requests.get(tickers_url).json()
    tickers = list(map(lambda x: [split_symbol(x['symbol']), float(x['askPrice']), float(x['bidPrice'])], response))
    return tickers
    
def fetch_orderbook(symbol):
    orderbook = requests.get(orderbook_url, {'symbol': symbol, 'limit' : orderbook_depth}).json()
    return orderbook
