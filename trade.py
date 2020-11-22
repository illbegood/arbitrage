import ccxt
import math
import networkx as nx


def trade(path, trade_args, G):
    exchange = ccxt.binance({ 'apiKey': '-',
        'secret': '-', })
    for i in range(len(path) - 1):
        x_curr = path[i]
        x_next = path[i + 1]
        symb_curr = x_curr.split('.')[0]
        symb_next = x_next.split('.')[0]
        market = ''
        if G[x_curr][x_next]['d'] == 'direct':
            market = symb_next + '/' + symb_curr
            price = trade_args[i][0]
            volume = trade_args[i][1]
            try:
                exchange.create_limit_buy_order(market, volume, price)
            except:
                time.sleep(0.05)
                exchange.create_limit_buy_order(market, volume, price)
        else:
            market = symb_curr + '/' + symb_next
            price = trade_args[i][0]
            volume = trade_args[i][1]
            try:
                exchange.create_limit_sell_order(market, volume, price)
            except:
                time.sleep(0.05)
                exchange.create_limit_sell_order(market, volume, price)
