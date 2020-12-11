import math
import binance
from collections import deque
from logger import write
from const import fee, precision, orderbook_depth
from traceback import format_exc

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def get_trade_args(graph, monograph, cycle, balance):
    logDeque = deque()
    try:
        logDeque.append('------------------------')
        logDeque.append(cycle)
        max_volume = balance
        all_orders = []
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
            if x_cur in monograph and x_next in monograph[x_cur]:
                symb = x_cur + x_next
                #expected_price = math.exp(-graph[x_cur][x_next])
                order = binance.fetch_orderbook(symb)['asks'][0]
                price, volume = float(order[0]), float(order[1])
                all_orders.append([price, volume])
                #if price > expected_price:
                #    logDeque.append(format_exc())
                #    logDeque.append(None)
                #    return None, None, logDeque
                if volume * price > max_volume:
                    max_volume /= price
                else:
                    max_volume = volume
                logDeque.append((x_next + ' volume, ', max_volume))
            else:
                symb = x_next + x_cur
                #expected_price = math.exp(-graph[x_next][x_cur])
                order = binance.fetch_orderbook(symb)['bids'][0]
                price, volume = float(order[0]), float(order[1])
                all_orders.append([price, volume])
                #if price < expected_price:
                #    logDeque.append(format_exc())
                #    logDeque.append(None)
                #    return None, None, logDeque
                if volume > max_volume:
                    max_volume *= price
                else:
                    max_volume = volume * price
                logDeque.append((x_next + ' volume, ', max_volume))
        return max_volume, all_orders, logDeque
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
        return None, None, logDeque
    
def trade(graph, monograph, cycle, balance):
    logDeque = deque()
    try:
        trade_balance, all_orders, innerLogDeque = get_trade_args(graph, monograph, cycle, balance)
        logDeque += innerLogDeque
        if logDeque[-1] is None:
            raise Exception('')
        if trade_balance < 5:
            raise Exception('low volume: ' + str(trade_balance))
        logDeque.append(('Total balance:', balance))
        logDeque.append(('Trade balance:', trade_balance))
        for i in range(len(cycle) - 1):
            x_cur = cycle[i]
            x_next = cycle[i + 1]
            if x_cur in monograph and x_next in monograph[x_cur]:
                symb = x_cur + '/' + x_next
                logDeque.append((symb, trade_balance))
                price = all_orders[i][0]
                order_volume = truncate(trade_balance / price, precision)
                logDeque.append(('BUY:', order_volume, price))
                trade_balance = order_volume * (1 - fee)
            else:
                symb = x_next + '/' + x_cur
                logDeque.append((symb, trade_balance))
                price = all_orders[i][0]
                order_volume = truncate(trade_balance, precision)
                logDeque.append(('SELL', order_volume, price))
                trade_balance = order_volume * price * (1 - fee)
        logDeque.append(('End balance:', trade_balance))
    except:
        if logDeque[-1] is not None:
            logDeque.append(format_exc())
            logDeque.append(None)
    finally:
        return logDeque
