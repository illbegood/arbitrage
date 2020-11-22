import math
from datetime import datetime
import networkx as nx
import cvxpy as cvx
import numpy as np

def pre_optimize(G, cycle, exchanges, depth):
    Volumes = np.zeros((len(cycle) - 1, depth))
    Rates = np.ones((len(cycle) - 1, depth))
    Orders = []
    Fees = np.ones((len(cycle) - 1,))

    for i in range(len(cycle) - 1):
        x_curr = cycle[i]
        x_next = cycle[i + 1]
        symb_curr, exch_curr = x_curr.split('.')
        symb_next = x_next.split('.')[0]
        exch = exchanges[exch_curr]
        if G[x_curr][x_next]['d'] == 'direct':
            symb = symb_next + '/' + symb_curr
            orderbook = exch.fetch_order_book(symb)['asks'][0:depth]
            #orderbook = exch.get_orderbook(market, depth_type='sell', depth=depth)
        else:
            symb = symb_curr + '/' + symb_next
            orderbook = exch.fetch_order_book(symb)['bids'][0:depth]
            #orderbook = exch.get_orderbook(market, depth_type='buy', depth=depth)'''
        Orders.append([])
        for j, order in enumerate(orderbook[:depth]):
            Volumes[i, j] = order[1]
            Rates[i, j] = order[0]
            Orders[i].append(order)

        Fees[i] = G[x_curr][x_next]['fee']
        if G[x_curr][x_next]['d'] == 'direct':
            Volumes[i] *= Rates[i]
            Rates[i] = 1 / Rates[i]
    return Volumes, Rates, Fees, Orders

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def set_trade_args(orders, coeffs, path, G, balance):
    trade_args = []
    previous_volume = balance
    sell_counter = 0
    fee = 1 - 0.001
    for i in range(len(path) - 1):
        x_curr = path[i]
        x_next = path[i+1]
        precision = float(G[x_curr][x_next]['p'])
        max_price = 0
        min_price = float('inf')
        volume = 0
        deal_type = ''
        if G[x_curr][x_next]['d'] == 'direct':
            deal_type = 'buy'
        else:
            deal_type = 'sell'
        for order, coeff in zip(orders[i], coeffs[i]):
            if (deal_type == 'buy'):
                if order[0] > max_price and coeff > 0.001:
                    max_price = order[0]
            else:
                if order[0] < min_price and coeff > 0.001:
                    min_price = order[0]
            if coeff > 0.001:
                volume += order[1] * coeff
        volume = truncate(volume, precision)
        if deal_type == 'buy':
            if max_price == 0:
                return None
            previous_volume = previous_volume / max_price
            if volume > previous_volume:
                volume = truncate(previous_volume, precision)
            trade_args.append((max_price, volume))
            sell_counter = 0
        else:
            if min_price == float('inf'):
                return None
            if sell_counter % 2 == 1:
                previous_volume = fee * trade_args[i-1][0] * trade_args[i-1][1]
            if volume > previous_volume:
                volume = truncate(previous_volume, precision)
            trade_args.append((min_price, volume))
            sell_counter += 1
        previous_volume = fee * volume

    print(trade_args[len(path) - 2][0] * trade_args[len(path) - 2][1])
    if (trade_args[len(path) - 2][0] * trade_args[len(path) - 2][1] > balance):
        return trade_args
    else:
        return None


def optimize(Volumes, R, Fees, Balances, solver):
    n, m = Volumes.shape
    X = cvx.Variable((n, m))

    constraints = [X >= 0, X <= Volumes]
    if Balances is not None:
        for i in range(n):
            if Balances[i] == 0:
                continue
            constraints.append(cvx.sum(X[i, :]) <= Balances[i])

    for i in range(1, n):
        # SUM IS CORRECT!!!!
        c = cvx.sum(X[i, :]) == Fees[i - 1] * cvx.sum(cvx.multiply(R[i - 1, :], X[i - 1, :].T))
        constraints.append(c)

    objective = cvx.Maximize(cvx.sum(cvx.multiply(R[-1, :], X[-1, :].T)) - cvx.sum(X[0, :]))
    prob = cvx.Problem(objective, constraints)
    prob.solve(solver)

    return prob

