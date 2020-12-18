import math
import binance
from collections import deque
from logger import write
from const import FEE, PRECISION, ORDERBOOK_DEPTH, RELEASE
from traceback import format_exc


def set_precision(f, n=PRECISION):
    return math.floor(f * 10 ** n) / 10 ** n


def truncate(f, min_lot):
    return min_lot * (f // min_lot)


def get_trade_args_iter(BUY, graph, x_cur, x_next, restrictions, orders, max_volume, expected_profit):
    logDeque = deque()
    try:
        symbol = x_next + x_cur if BUY else x_cur + x_next
        min_lot, min_notional = restrictions[symbol][0], restrictions[symbol][1]
        order = binance.fetch_orderbook(symbol)
        if len(order) == 0:
            logDeque.append("NO ORDERS")
            logDeque.append(None)
            return None, None, logDeque
        order = order['asks' if BUY else 'bids'][0]
        price, volume = float(order[0]), float(order[1])
        orders.append([price, volume])
        logDeque.append((symbol, '(BUY)' if BUY else '(SELL)'))
        logDeque.append(('\t', 'min_lot:', min_lot,
                         'min_notional:', min_notional))
        logDeque.append(('\t', 'price', price, 'volume', volume))
        logDeque.append(('\t', 'previous volume', max_volume))
        if BUY:
            if volume * price > max_volume:
                logDeque.append(('\t', 'buying with whole available volume'))
                max_volume = truncate(max_volume / price, min_lot)
            else:
                logDeque.append(('\t', 'buying whole volume'))
                max_volume = truncate(volume, min_lot)
            if max_volume * price < min_notional:
                logDeque.append(('\t', 'warning: resulting volume',
                                 max_volume, 'is smaller than', min_notional))
                max_volume = 0
        else:
            if volume > max_volume:
                logDeque.append(('\t', 'selling with whole available volume'))
                max_volume = truncate(price * max_volume, min_lot)
            else:
                logDeque.append(('\t', 'selling whole volume'))
                max_volume = truncate(price * volume, min_lot)
            if max_volume < min_notional:
                logDeque.append(('\t', 'warning: resulting volume',
                                 max_volume, 'is smaller than', min_notional))
                max_volume = 0

        expected_profit = expected_profit / \
            (price / (1 - FEE)) if BUY else expected_profit * (price * (1 - FEE))
        if BUY:
            record = ('\t', 'resulting price:', price /
                      (1 - FEE), 'resulting volume:', max_volume)
        else:
            record = ('\t', 'resulting price:', price *
                      (1 - FEE), 'resulting volume:', max_volume)
        logDeque.append(record)  # fees included
        return max_volume, expected_profit, logDeque
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)


def get_trade_args(graph, monograph, cycle, balance, restrictions):
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
            max_volume, expected_profit, innerLogDeque = get_trade_args_iter(
                BUY, graph, x_cur, x_next, restrictions, orders, max_volume, expected_profit)
            logDeque += innerLogDeque
        logDeque.append(('expected_profit: ', expected_profit))
        return expected_profit, max_volume, orders, logDeque
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
        return None, None, None, logDeque


def trade_iter(BUY, x_cur, x_next, trade_balance, price, restrictions):
    logDeque = deque()
    symbol = x_next + x_cur if BUY else x_cur + x_next
    min_lot = restrictions[symbol][0]
    order_volume = trade_balance / price if BUY else trade_balance
    order_volume = truncate(order_volume, min_lot)
    logDeque.append((symbol, '(BUY)' if BUY else '(SELL)'))
    logDeque.append(('volume', order_volume, 'price', price,
                     'previous volume', trade_balance))
    if BUY:
        if RELEASE:
            print(binance.limit_order(symbol, 'BUY',
                                      order_volume, set_precision(price)))
    else:
        if RELEASE:
            print(binance.limit_order(symbol, 'SELL',
                                      order_volume, set_precision(price)))
    trade_balance = order_volume * \
        (1 - FEE) if BUY else order_volume * price * (1 - FEE)
    return trade_balance, logDeque


def trade(graph, monograph, cycle, restrictions):
    logDeque = deque()
    logDeque.append('------------------------')
    balance = 1000000000  # binance.fetch_balance()
    try:
        expected_profit, trade_balance, orders, innerLogDeque = get_trade_args(
            graph, monograph, cycle, balance, restrictions)
        logDeque += innerLogDeque

        if trade_balance < 1:
            logDeque.append('low volume: ' + str(trade_balance))
            return logDeque
        if expected_profit <= 1:
            logDeque.append('no profit expected: ' + str(expected_profit))
            return logDeque

        logDeque.append(('Total balance:', balance))
        logDeque.append(('Trade balance:', trade_balance))
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
            BUY = x_cur in monograph.keys() and x_next in monograph[x_cur]
            trade_balance, innerLogDeque = trade_iter(
                BUY, x_cur, x_next, trade_balance, orders[i][0], restrictions)
            logDeque += innerLogDeque
            if logDeque[-1] is None:
                return logDeque
        logDeque.append(('End balance:', trade_balance))
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
        return logDeque
