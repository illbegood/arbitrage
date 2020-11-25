import ccxt
import numpy as np
import math

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def get_volume_and_orderbooks(graph, cycle, balance, depth):
    max_volume = balance
    for i in range(len(cycle) - 1):
        x_cur = cycle[i]
        x_next = cycle[i + 1]
        all_orderbooks = []
        if graph[x_curr][x_next]['d'] == 'direct':
            symb = x_next + '/' + x_cur
            orderbook = exch.fetch_order_book(symb)['asks'][0:depth]
            all_orderbooks.append(orderbook)
            volume_in_current_currency = 0
            volume_in_next_currency = 0
            for order in orderbook:
                price = order[0]
                volume = order[1]
                if volume_in_current_currency + volume * price > max_volume:
                    max_volume = (max_volume - cur_symbol_volume) / price + volume_in_next_currency
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
                    max_volume = (max_volume - cur_symbol_volume) * price + volume_in_next_currency
                    volume_in_current_currency = float('inf')
                    break
                volume_in_current_currency += volume
                volume_in_next_currency += volume * price
            if volume_in_current_currency < max_volume:
                max_volume = volume_in_next_currency
        return max_volume, all_orderbooks
    
def process_cycle(graph, cycle, exch, balance, orderbook_depth, precision):
    trade_balance, all_orderbooks = get_volume_and_orderbooks(graph, cycle, balance, orderbook_depth)
    fee = 0.001
    next_cur_balance = 0
    for i in range(len(cycle) - 1):
        x_cur = cycle[i]
        x_next = cycle[i + 1]
        if graph[x_curr][x_next]['d'] == 'direct':
            symb = x_next + '/' + x_cur
            orderbook = all_orderbooks[i]
            order_idx = 0
            while (trade_balance >= precision):
                price = orderbook[order_idx][0]
                volume = orderbook[order_idx][1] * price
                if volume > trade_balance:
                    order_volume = truncate(trade_balance / price, precision)
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    print('BUY:', order_volume, price)
                    trade_balance -= order_volume * price * (1 + fee)
                    next_cur_balance += order_volume * (1 - fee)
                else:
                    order_volume = truncate(converted_volume / price, precision)
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    print('BUY:', order_volume, price)
                    trade_balance -= order_volume * price * (1 + fee)
                    next_cur_balance += order_volume * (1 - fee)
                    order_idx += 1
        else:
            symb = x_cur + '/' + x_next
            orderbook = all_orderbooks[i]
            order_idx = 0
            while (trade_balance >= precision):
                price = orderbook[order_idx][0]
                volume = orderbook[order_idx][1]
                if volume > trade_balance:
                    order_volume = truncate(trade_balance, precision)
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    print('SELL:', order_volume, price)
                    trade_balance -= order_volume * (1 + fee)
                    next_cur_balance += order_volume * price * (1 - fee)
                else:
                    order_volume = truncate(volume, precision)
                    #exchange.create_limit_buy_order(market, order_volume, price)
                    print('SELL:', order_volume, price)
                    trade_balance -= order_volume * (1 + fee)
                    next_cur_balance += order_volume * price * (1 - fee)
                    order_idx += 1
        trade_balance = next_cur_balance
        
