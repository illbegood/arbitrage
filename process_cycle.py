import ccxt
import numpy as np
import math
from collections import deque
from logger import write

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def get_volume_and_orderbooks(graph, monograph, cycle, balance, exch, depth):
    max_volume = balance
    all_orderbooks = []
    for i in range(len(cycle) - 1):
        x_cur = cycle[i]
        x_next = cycle[i + 1]
        if x_cur in monograph.keys():
            symb = x_next + '/' + x_cur
            orderbook = exch.fetch_order_book(symb)['asks'][0:depth]
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
        else:
            symb = x_cur + '/' + x_next
            orderbook = exch.fetch_order_book(symb)['bids'][0:depth]
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
    return max_volume, all_orderbooks
    
def process_cycle(graph, monograph, cycle, exch, balance, orderbook_depth, precision):
    #logDict = {}
    logDeque = deque()
    trade_balance, all_orderbooks = get_volume_and_orderbooks(graph, monograph, cycle, balance, exch, orderbook_depth)
    fee = 0#0.001
    #logDict['balance'] = balance
    logDeque.append(('Total balance:', balance))
    #print('Total balance:', balance)
    #logDict['trade_balance'] = trade_balance
    logDeque.append(('Trade balance:', trade_balance))
    #print('Trade balance:', trade_balance)
    #transactionList = []
    #logDict['transactionList'] = transactionList
    #symbList = []
    #logDict['symbList'] = symbList
    for i in range(len(cycle) - 1):
        x_cur = cycle[i]
        x_next = cycle[i + 1]
        next_cur_balance = 0
        if x_cur in monograph.keys():
            symb = x_next + '/' + x_cur
            #symbList.append(symb)
            logDeque.append((symb, trade_balance))
            #print(symb, trade_balance)
            orderbook = all_orderbooks[i]
            order_idx = 0
            while (order_idx < orderbook_depth):
                price = orderbook[order_idx][0]
                volume = orderbook[order_idx][1] * price
                if volume > trade_balance:
                    order_volume = truncate(trade_balance / price, precision)
                    #Eto nuzho ili net?
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    #transactionList.append(('BUY', order_volume, price))
                    logDeque.append(('BUY:', order_volume, price))
                    #print('BUY:', order_volume, price)
                    trade_balance -= order_volume * price * (1 + fee)
                    next_cur_balance += order_volume * (1 - fee)
                    break
                else:
                    order_volume = truncate(volume / price, precision)
                    #Eto nuzho ili net?
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    #transactionList.append(('BUY', order_volume, price))
                    logDeque.append(('BUY', order_volume, price))
                    #print('BUY:', order_volume, price)
                    trade_balance -= order_volume * price * (1 + fee)
                    next_cur_balance += order_volume * (1 - fee)
                    order_idx += 1
        else:
            symb = x_cur + '/' + x_next
            #symbList.append(symb)
            logDeque.append((symb, trade_balance))
            #print(symb, trade_balance)
            orderbook = all_orderbooks[i]
            order_idx = 0
            while (order_idx < orderbook_depth):
                price = orderbook[order_idx][0]
                volume = orderbook[order_idx][1]
                if volume > trade_balance:
                    order_volume = truncate(trade_balance, precision)
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    #transactionList.append(('SELL', order_volume, price))
                    logDeque.append(('SELL', order_volume, price))
                    #print('SELL:', order_volume, price)
                    trade_balance -= order_volume * (1 + fee)
                    next_cur_balance += order_volume * price * (1 - fee)
                    break
                else:
                    order_volume = truncate(volume, precision)
                    #Eto nuzho ili net?
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    #transactionList.append(('SELL', order_volume, price))
                    logDeque.append(('SELL', order_volume, price))
                    #print('SELL:', order_volume, price)
                    trade_balance -= order_volume * (1 + fee)
                    next_cur_balance += order_volume * price * (1 - fee)
                    order_idx += 1
        trade_balance = next_cur_balance
    #logDict['end_balance'] = trade_balance
    logDeque.append(('End balance:', trade_balance))
    #print('End balance:', trade_balance)
    write(logDeque)
