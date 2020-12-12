import math
import binance
from collections import deque
from logger import write
from const import FEE, PRECISION, ORDERBOOK_DEPTH
from traceback import format_exc

def truncate(f, n = PRECISION):
    return math.floor(f * 10 ** n) / 10 ** n

def get_trade_args_iter(SELL, graph, x_cur, x_next, orders, max_volume, expected_profit):
    logDeque = deque()
    symb = x_cur + x_next if SELL else x_next + x_cur
    order = binance.fetch_orderbook(symb)
    order = order['bids' if SELL else 'asks'][0]
    price, volume = float(order[0]), float(order[1])
    orders.append([price, volume])
    if SELL:
        if volume > max_volume:
            max_volume *= price
        else:
            max_volume = volume * price
    else:
        if volume * price > max_volume:
            max_volume /= price
        else:
            max_volume = volume
    expected_profit = expected_profit * (price * (1 - FEE)) if SELL else expected_profit / (price * (1 - FEE))
    expected_price = math.exp(graph[x_next][x_cur] if SELL else graph[x_cur][x_next])
    record = ('SELL ' if SELL else 'BUY ' + symb + ' price, expected price: ', price * (1 - FEE), expected_price)
    logDeque.append(record) # fees included
    logDeque.append((x_next + ' volume, ', max_volume))
    return max_volume, expected_profit, logDeque


def get_trade_args(graph, monograph, cycle, balance):
    logDeque = deque()
    try:
        logDeque.append(cycle)
        max_volume = balance
        expected_profit = 1
        orders = []
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
<<<<<<< HEAD
            SELL = x_cur in monograph and x_next in monograph[x_cur]
            max_volume, expected_profit, innerLogDeque = get_trade_args_iter(SELL, graph, x_cur, x_next, orders, max_volume, expected_profit)
            logDeque += innerLogDeque
=======
            # Sell Case:
            # Imagine cycle [USDT BTC ETH USDT]
            # x_cur = ETH
            # x_next = USDT
            # binance symbol ETHUSDT = x_cur + x_next
            if x_cur in monograph and x_next in monograph[x_cur]:
                symb = x_cur + x_next
                order = binance.fetch_orderbook(symb)['bids'][0]
                price, volume = float(order[0]), float(order[1])
                orders.append([price, volume])
                if volume > max_volume:
                    max_volume *= price
                else:
                    max_volume = volume * price
                expected_profit *= (price * (1 + fee))
                expected_price = math.exp(-graph[x_next][x_cur])
                logDeque.append(('SELL ' + symb + ' price, expected price: ', price * (1 - fee), expected_price)) # fees included
                logDeque.append((x_next + ' volume, ', max_volume))
            # Buy Case:
            # Imagine cycle [USDT BTC ETH USDT]
            # x_cur = USDT
            # x_next = BTC
            # binance symbol BTCUSDT = x_next + x_cur
            else:
                symb = x_next + x_cur
                order = binance.fetch_orderbook(symb)['asks'][0]
                price, volume = float(order[0]), float(order[1])
                orders.append([price, volume])
                if volume * price > max_volume:
                    max_volume /= price
                else:
                    max_volume = volume
                expected_profit /= (price * (1 - fee))
                expected_price = 1 / math.exp(-graph[x_next][x_cur])
                logDeque.append(('BUY ' + symb + ' price, expected price: ', price * (1 - fee), expected_price)) # fees included
                logDeque.append((x_next + ' volume, ', max_volume))
>>>>>>> 401c3f4c0c18abf2c1fbd7f7a9635d469e623298
        logDeque.append(('expected_profit: ', expected_profit))
        return expected_profit, max_volume, orders, logDeque
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
        return None, None, None, logDeque

def trade_iter(SELL, x_cur, x_next, trade_balance, price):
    logDeque = deque()
    symb = x_cur + x_next if SELL else x_next + x_cur
    logDeque.append((symb, trade_balance))
    order_volume = trade_balance if SELL else trade_balance / price
    order_volume = truncate(order_volume)
    logDeque.append(('SELL:' if SELL else 'BUY:', order_volume, price))
    trade_balance = order_volume * price * (1 - FEE) if SELL else order_volume * (1 - FEE)
    return trade_balance, logDeque

def trade(graph, monograph, cycle, balance):
    logDeque = deque()
    logDeque.append('------------------------')
    try:
        expected_profit, trade_balance, orders, innerLogDeque = get_trade_args(graph, monograph, cycle, balance)
        logDeque += innerLogDeque
        '''
        if trade_balance < 5:
            logDeque.append('low volume: ' + str(trade_balance))
            return
        if expected_profit <= 1:
            logDeque.append('no profit expected: ' + str(expected_profit))
            return
        '''
        logDeque.append(('Total balance:', balance))
        logDeque.append(('Trade balance:', trade_balance))
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
<<<<<<< HEAD
            SELL = x_cur in monograph and x_next in monograph[x_cur]
            trade_balance, innerLogDeque = trade_iter(SELL, x_cur, x_next, trade_balance, orders[i][0])
            logDeque += innerLogDeque
=======
            # Sell Case
            if x_cur in monograph and x_next in monograph[x_cur]:
                symb = x_cur + x_next
                logDeque.append((symb, trade_balance))
                price = orders[i][0]
                order_volume = truncate(trade_balance, precision)
                logDeque.append(('SELL:', order_volume, price))
                trade_balance = order_volume * price * (1 - fee)
            # Buy Case
            else:
                symb = x_next + x_cur
                logDeque.append((symb, trade_balance))
                price = orders[i][0]
                order_volume = truncate(trade_balance / price, precision)
                logDeque.append(('BUY', order_volume, price))
                trade_balance = order_volume * (1 - fee)
>>>>>>> 401c3f4c0c18abf2c1fbd7f7a9635d469e623298
        logDeque.append(('End balance:', trade_balance))
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
    finally:
        return logDeque
