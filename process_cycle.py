import ccxt
import numpy as np
import math
from collections import deque
from logger import write
from const import fee, precision, orderbook_depth
from traceback import format_exc

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n
    
def convert_to_usdt(graph, monograph, currency, volume):
    if currency != 'USDT':
        if currency in monograph.keys() and 'USDT' in monograph[currency]:
            #symb = 'USDT' + '/' + currency
            price = math.exp(-graph['USDT'][currency])
        else:
            price = math.exp(-graph[currency]['USDT'])
        return price * volume
    return volume

def get_volume_and_orderbooks(graph, monograph, cycle, balance, exch):
    logDeque = deque()
    try:
        logDeque.append(cycle)
        max_volume = balance
        all_orderbooks = []
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
            if x_cur in monograph and x_next in monograph[x_cur]:
                symb = x_cur + '/' + x_next
                orderbook = exch.fetch_order_book(symb)['asks'][0:orderbook_depth]
                all_orderbooks.append(orderbook)
                volume_in_current_currency = 0
                volume_in_next_currency = 0
                for order in orderbook:
                    price = order[0]
                    volume = order[1]
                    if volume_in_current_currency + volume * price > max_volume:
                        max_volume = (max_volume - volume_in_current_currency) / price + volume_in_next_currency
                        volume_in_current_currency = float('inf')
                        break
                    volume_in_current_currency += volume * price
                    volume_in_next_currency += volume
                if volume_in_current_currency < max_volume:
                    max_volume = volume_in_next_currency
                max_volume_usdt = convert_to_usdt(graph, monograph, x_next, max_volume)
                logDeque.append((symb, orderbook))
                logDeque.append((x_next + ' volume, ' + x_next + ' volume in USD', max_volume, max_volume_usdt))
            else:
                symb = x_next + '/' + x_cur
                orderbook = exch.fetch_order_book(symb)['bids'][0:orderbook_depth]
                all_orderbooks.append(orderbook)
                volume_in_current_currency = 0
                volume_in_next_currency = 0
                for order in orderbook:
                    price = order[0]
                    volume = order[1]
                    if volume_in_current_currency + volume > max_volume:
                        max_volume = (max_volume - volume_in_current_currency) * price + volume_in_next_currency
                        volume_in_current_currency = float('inf')
                        break
                    volume_in_current_currency += volume
                    volume_in_next_currency += volume * price
                if volume_in_current_currency < max_volume:
                    max_volume = volume_in_next_currency
                max_volume_usdt = convert_to_usdt(graph, monograph, x_next, max_volume)
                logDeque.append((symb, orderbook))
                logDeque.append((x_next + ' volume, ' + x_next + ' volume in USD', max_volume, max_volume_usdt))
        return max_volume, all_orderbooks, logDeque
    except:
        if logDeque[-1] is not None: 
            logDeque.append(format_exc())
            logDeque.append(None)
        return None, None, logDeque
    
def process_cycle(graph, monograph, cycle, exch, balance):
    logDeque = deque()
    try:
        trade_balance, all_orderbooks, innerLogDeque = get_volume_and_orderbooks(graph, monograph, cycle, balance, exch)
        logDeque += innerLogDeque
        if logDeque[-1] is None:
            raise Exception('')
        logDeque.append(('Total balance:', balance))
        logDeque.append(('Trade balance:', trade_balance))
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
            next_cur_balance = 0
            if x_cur in monograph and x_next in monograph[x_cur]:
                symb = x_cur + '/' + x_next
                logDeque.append((symb, trade_balance))
                orderbook = all_orderbooks[i]
                order_idx = 0
                while (order_idx < orderbook_depth):
                    price = orderbook[order_idx][0]
                    volume = orderbook[order_idx][1] * price
                    if volume > trade_balance:
                        order_volume = truncate(trade_balance / price, precision)
                        logDeque.append(('BUY:', order_volume, price))
                        trade_balance -= order_volume * price * (1 + fee)
                        next_cur_balance += order_volume * (1 - fee)
                        break
                    else:
                        order_volume = truncate(volume / price, precision)
                        logDeque.append(('BUY', order_volume, price))
                        trade_balance -= order_volume * price * (1 + fee)
                        next_cur_balance += order_volume * (1 - fee)
                        order_idx += 1
            else:
                symb = x_next + '/' + x_cur
                logDeque.append((symb, trade_balance))
                orderbook = all_orderbooks[i]
                order_idx = 0
                while (order_idx < orderbook_depth):
                    price = orderbook[order_idx][0]
                    volume = orderbook[order_idx][1]
                    if volume > trade_balance:
                        order_volume = truncate(trade_balance, precision)
                        logDeque.append(('SELL', order_volume, price))
                        trade_balance -= order_volume * (1 + fee)
                        next_cur_balance += order_volume * price * (1 - fee)
                        break
                    else:
                        order_volume = truncate(volume, precision)
                        logDeque.append(('SELL', order_volume, price))
                        trade_balance -= order_volume * (1 + fee)
                        next_cur_balance += order_volume * price * (1 - fee)
                        order_idx += 1
            trade_balance = next_cur_balance
        logDeque.append(('End balance:', trade_balance))
    except:
        if logDeque[-1] is not None: 
            logDeque.append(format_exc())
            logDeque.append(None)
    finally:
        return logDeque
    
