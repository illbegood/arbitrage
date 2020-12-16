import numpy as np
import requests
from urllib.parse import urlencode
import hashlib
import hmac
import time
import json
from const import ORDERBOOK_DEPTH
from keys import API_KEY, SECRET_KEY

BINANCE_API_V3 = 'https://api.binance.com/api/v3/'
SYMBOLS_URL = BINANCE_API_V3 + 'exchangeInfo'
TICKERS_URL = BINANCE_API_V3 + 'ticker/24hr'
ORDERBOOK_URL = BINANCE_API_V3 + 'depth'
ACCOUNT_URL = BINANCE_API_V3 + 'account'
ORDER_URL = BINANCE_API_V3 + 'order'
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

def get_timestamp():
    return int(time.time() * 1000)

def hashing(query_string):
    return hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def dispatch_request(http_method):
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json;charset=utf-8',
        'X-MBX-APIKEY': API_KEY
    })
    return {
        'GET': session.get,
        'DELETE': session.delete,
        'PUT': session.put,
        'POST': session.post,
    }.get(http_method, 'GET')

# used for sending request requires the signature
def send_signed_request(http_method, url_path, payload={}):
    query_string = urlencode(payload, True)
    if query_string:
        query_string = "{}&timestamp={}".format(query_string, get_timestamp())
    else:
        query_string = 'timestamp={}'.format(get_timestamp())
    url = url_path + '?' + query_string + '&signature=' + hashing(query_string)
    params = {'url': url, 'params': {}}
    response = dispatch_request(http_method)(**params)
    return response.json()
    
def find_usdt(assets):
    for item in assets:
        if item['asset'] == 'USDT':
            return item

def fetch_balance():
    assets = send_signed_request('GET', ACCOUNT_URL)['balances']
    return float(find_usdt(assets)['free'])
    
def limit_order(symbol, side, volume, price):
    params = {
        "symbol": symbol,
        "side": side, # In Capital Letters, e.g. BUY
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": volume,
        "price": str(price)
    }
    send_signed_request('POST', ORDER_URL, params)
