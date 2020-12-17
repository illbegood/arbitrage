import math
import binance
from collections import deque
from logger import write
from const import FEE, PRECISION, ORDERBOOK_DEPTH
from traceback import format_exc

#def truncate(f, n = PRECISION):
#    return math.floor(f * 10 ** n) / 10 ** n
    
def truncate(f, min_lot):
    return min_lot * (f // min_lot)

def get_trade_args_iter(BUY, graph, x_cur, x_next, lot_restrictions, orders, max_volume, expected_profit):
    logDeque = deque()
    symbol = x_next + x_cur if BUY else x_cur + x_next
    min_lot = lot_restrictions[symbol]
    order = binance.fetch_orderbook(symbol)
    order = order['asks' if BUY else 'bids'][0]
    price, volume = float(order[0]), float(order[1])
    orders.append([price, volume])
    if BUY:
        if volume * price > max_volume:
            max_volume = truncate(max_volume / price, min_lot)
        else:
            max_volume = truncate(volume, min_lot)
    else:
        if volume > max_volume:
            max_volume = truncate(price * max_volume, min_lot)
        else:
            max_volume = truncate(price * volume, min_lot)

    expected_profit = expected_profit / (price / (1 - FEE)) if BUY else expected_profit * (price * (1 - FEE))
    expected_price = math.exp(-graph[x_cur][x_next])
    if BUY:
        record = ('BUY ' + symbol + ' price, expected price: ', price / (1 - FEE), 1 / expected_price)
    else:
        record = ('SELL ' + symbol + ' price, expected price: ', price * (1 - FEE), expected_price)
    logDeque.append(record) # fees included
    logDeque.append((x_next + ' volume, ', max_volume))
    return max_volume, expected_profit, logDeque


def get_trade_args(graph, monograph, cycle, balance, lot_restrictions):
    logDeque = deque()
    try:
        logDeque.append(cycle)
        max_volume = balance
        expected_profit = 1
        orders = []
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
            BUY = x_cur in monograph.keys() and x_next in monograph[x_cur]
            max_volume, expected_profit, innerLogDeque = get_trade_args_iter(BUY, graph, x_cur, x_next, lot_restrictions, orders, max_volume, expected_profit)
            logDeque += innerLogDeque
        logDeque.append(('expected_profit: ', expected_profit))
        return expected_profit, max_volume, orders, logDeque
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
        return None, None, None, logDeque

def trade_iter(BUY, x_cur, x_next, trade_balance, price, lot_restrictions):
    logDeque = deque()
    symbol = x_next + x_cur if BUY else x_cur + x_next
    logDeque.append((symbol, trade_balance))
    min_lot = lot_restrictions[symbol]
    order_volume = trade_balance / price if BUY else trade_balance
    order_volume = truncate(order_volume, min_lot)
    if BUY:
        print(binance.limit_order(symbol, 'BUY', order_volume, price))
        logDeque.append(('BUY:', order_volume, price))
    else:
        print(binance.limit_order(symbol, 'SELL', order_volume, price))
        logDeque.append(('SELL:', order_volume, price))
    trade_balance = order_volume * (1 - FEE) if BUY else order_volume * price * (1 - FEE)
    return trade_balance, logDeque

def trade(graph, monograph, cycle, lot_restrictions):
    logDeque = deque()
    logDeque.append('------------------------')
    balance = binance.fetch_balance()
    try:
        expected_profit, trade_balance, orders, innerLogDeque = get_trade_args(graph, monograph, cycle, balance, lot_restrictions)
        logDeque += innerLogDeque
        
        if trade_balance < 1:
            logDeque.append('low volume: ' + str(trade_balance))
            return
        if expected_profit <= 1:
            logDeque.append('no profit expected: ' + str(expected_profit))
            return
        
        logDeque.append(('Total balance:', balance))
        logDeque.append(('Trade balance:', trade_balance))
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
            BUY = x_cur in monograph.keys() and x_next in monograph[x_cur]
            trade_balance, innerLogDeque = trade_iter(BUY, x_cur, x_next, trade_balance, orders[i][0], lot_restrictions)
            logDeque += innerLogDeque
        logDeque.append(('End balance:', trade_balance))
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
    finally:
        return logDeque
