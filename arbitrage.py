import ccxt
import math
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import cvxpy as cvx
import numpy as np

import time

import logging
import logging.config
import logging.handlers
from multiprocessing.pool import ThreadPool
import multiprocessing

from telegram.ext import Updater, CommandHandler

def fetch_exchange(exch_name, exch):
    nodes = set()
    edges = []
    # load markets
    exch.load_markets(True)
    #huobi.load_markets(True)

    if (exch.has['fetchTickers']):
        exch_tickers = exch.fetch_tickers()
        for symbol in exch_tickers.keys():
            try:
                node_to, node_from = symbol.split('/')
                node_to += '.' + exch_name
                node_from += '.' + exch_name
                nodes.add(node_to)
                nodes.add(node_from)
                if (exch_name == 'binance'):
                    try:
                        w_to = -math.log(1 / float(exch_tickers[symbol]['info']['askPrice']))
                        w_from = - math.log(float(exch_tickers[symbol]['info']['askPrice']))
                        fee = 1 - 0.0001
                    except:
                        w_to = float('inf')
                        w_from = float('inf')
                        fee = 0
                else:
                    try:
                        w_to = -math.log(1 / float(exch_tickers[symbol]['ask']))
                        w_from = -math.log(float(exch_tickers[symbol]['ask']))
                        fee = 1 - 0.00026
                    except:
                        w_to = float('inf')
                        w_from = float('inf')
                        fee = 0
                edges.append((node_from, node_to, dict(c='buy', d='direct', weight=w_to, fee=fee)))
                edges.append((node_to, node_from, dict(c='sell', d='reverse', weight=w_from, fee=fee)))
            except:
                print('symbol error')
    return nodes, edges

def neg_cycle_handler(G, pred, dist, source, v):
    n = len(G)
    for _ in range(n):
        v = pred[v]
    t = v
    path = []
    while True:
        t = pred[t]
        path.append(t)

        if t == v:
            break
    path.reverse()
    return tuple(path)


def bellman_ford(G, source, weight='weight'):
    if source not in G:
        raise KeyError("Node %s is not found in the graph" % source)

    for u, v, attr in G.selfloop_edges(data=True):
        if attr.get(weight, 1) < 0:
            raise nx.NetworkXUnbounded("Negative cost cycle detected.")

    dist = {source: 0}
    pred = {source: None}

    if len(G) == 1:
        return pred, dist

    return _bellman_ford_relaxation(G, pred, dist, [source], weight)


def _bellman_ford_relaxation(G, pred, dist, source, weight):
    from collections import deque
    if G.is_multigraph():
        def get_weight(edge_dict):
            return min(eattr.get(weight, 1) for eattr in edge_dict.values())
    else:
        def get_weight(edge_dict):
            return edge_dict.get(weight, 1)

    G_succ = G.succ if G.is_directed() else G.adj
    inf = float('inf')
    n = len(G)
    cycles = set()
    count = {}
    q = deque(source)
    in_q = set(source)
    counter = 0
    fee = -math.log(1 - 0.00026)
    #fee = - np.log2(0.9975)
    while q and counter <= n * n:
        counter += 1
        u = q.popleft()
        in_q.remove(u)
        # Skip relaxations if the predecessor of u is in the queue.
        if pred[u] not in in_q:
            dist_u = dist[u]
            for v, e in G_succ[u].items():
                dist_v = dist_u + get_weight(e) + fee
                if dist_v < dist.get(v, inf):
                    if v not in in_q:
                        q.append(v)
                        in_q.add(v)
                        count_v = count.get(v, 0) + 1
                        if (count_v == n):
                            #print("Negative cost cycle detected.")
                            dist[v] = dist_v
                            pred[v] = u
                            vs = neg_cycle_handler(G, pred, dist, source, v)
                            if len(vs) > 2:
                                cycles.add(vs)
                            for x in vs:
                                count[v] = n
                        if (count_v == 1):
                            pred[v] = u
                            dist[v] = dist_v
                            if ((len(pred) > 2) and (pred[pred[v]] in G_succ[v].keys())):
                                suc = pred[pred[v]]
                                w1 = float(G_succ[suc][pred[v]]['weight'])
                                w2 = float(G_succ[pred[v]][v]['weight'])
                                w3 = float(G_succ[v][suc]['weight'])
                                if (w1 + w2 + w3 < 0):
                                    vs = []
                                    vs.append(suc)
                                    vs.append(pred[v])
                                    vs.append(v)
                                    cycles.add(tuple(vs))
                        count[v] = count_v
                    dist[v] = dist_v
                    pred[v] = u
    # print_vertexes(count, n)
    paths = [list(x) for x in cycles]
    for path in paths:
        p = path.copy()
        for i in range(len(p) - 1):
            p.append(p.pop(0))
            try:
                paths.remove(p)
            except ValueError:
                break
    return paths
    
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
            symb_curr, exch_curr = x_curr.split('.')
            symb_next = x_next.split('.')[0]
            exch = exchanges[exch_curr]
            symb = symb_next + '/' + symb_curr
            orderbook = exch.fetch_order_book(symb)['asks'][0:depth]
            #orderbook = exch.get_orderbook(market, depth_type='sell', depth=depth)
        else:
            symb_curr, exch_curr = x_curr.split('.')
            symb_next = x_next.split('.')[0]
            exch = exchanges[exch_curr]
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

def trade(path, orders, coeffs, G, exch_dict):
    exchange = exch_dict['kraken']
    for i in range(len(path) - 1):
        x_curr = path[i]
        x_next = path[i + 1]
        symb_curr = x_curr.split('.')[0]
        symb_next = x_next.split('.')[0]
        if G[x_curr][x_next]['d'] == 'direct':
            market = symb_next + '/' + symb_curr
            for order, coeff in zip(orders[i], coeffs[i]):
                # print(market, order[0], coeff, order[1])
                # print(type(market), type(order[0]), type(coeff), type(order[1]))
                if coeff > 0.001:
                    #binance.buy(market, order[0]*coeff, order[1])
                    exchange.create_limit_buy_order(market, float(order[1]) * coeff, float(order[0]))
        else:
            market = symb_curr + '/' + symb_next
            for order, coeff in zip(orders[i], coeffs[i]):
                # print(market, order[0], coeff, order[1])
                # print(type(market), type(order[0]), type(coeff), type(order[1]))
                if coeff > 0.001:
                    exchange.create_limit_sell_order(market, float(order[1]) * coeff, float(order[0]))
                # exchange.sell(market, order[0]*coeff, order[1])

def opt_parallel(args):
    kraken = ccxt.kraken({
    'apiKey': '-',
    'secret': '-',})
    exch_dict = {'kraken':kraken}
    G = args[0]
    path = args[1]
    depth = args[2]
    cycle = cycle_handler(path)
    if (cycle != None):
        try:
            Volumes, Rates, Fees, Orders = pre_optimize(G, cycle, exch_dict, depth)
            usd_balance = kraken.fetch_balance()['USD']['free']
            Balances = [usdt_balance, 0, 0, 0, 0, 0, 0, 0]
            prob = optimize(Volumes, Rates, Fees, Balances,'ECOS')
            x = prob.variables()[0]
            start_volume = x.value[0].sum()
            profit_percents = 100 * prob.value / start_volume
            Volumes[Volumes == 0] = 1.0
            coeffs = x.value / Volumes
            corrupted_indexes = np.isnan(coeffs) + np.abs(coeffs) == np.inf  # this is logical OR
            coeffs[corrupted_indexes] = 0.0
            trade_args = (Orders, coeffs)
            return [prob.value, profit_percents, prob, trade_args, cycle, usd_balance]
        except:
            #print('Solver failed')
            return None
    return None

def cycle_handler(cycle):
    if ('USD.kraken' in cycle):
        start_currency = 'USD.kraken'
    else:
        return None
    while(cycle[0] != start_currency):
            cycle = cycle[-1:] + cycle[:-1]
    cycle = cycle + [cycle[0]]
    return cycle

def do_main(bot, job):
    kraken = ccxt.kraken({
    'apiKey': '!',
    'secret': '!',})
    logger = logging.getLogger("TelegramApp.do_main")
    start_time = time.time()
    exch_dict = {'kraken': kraken} #'huobi': huobi}
    nodes, edges = fetch_exchange('kraken', kraken)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    depth = 10
    start_with = 'BTC.kraken'
    paths = bellman_ford(G, start_with)
    #time.sleep(0.5)
    args = [[G, path, depth] for path in paths]
    pool = multiprocessing.Pool(processes=6)
    report = {}
    for res in pool.imap_unordered(opt_parallel, args):
        if res is None:
            continue
        else:
            profit_value, profit_percents, prob, trade_args, cycle, usd_balance = res
            if (100 * profit_value / profit_percents > 0.9 * usd_balance):
                trade(cycle, trade_args[0], trade_args[1], G, exch_dict)
                bot.send_message(chat_id=job.context['chat_id'], text='trade executed')
                report[str(cycle)] = {'profit_percents': profit_percents, 'profit_value': profit_value, 'coeffs': trade_args[1], 'orders': trade_args[0]}
                #trade(cycle, trade_args[0], trade_args[1], G, exch_dict)
    end_time = time.time() - start_time
    if (len(report) > 0):
        for key in report.keys():
            time_info = 'processing time: ' + str(end_time) + '\n'
            cycle_info = key + '\n'
            percent_info = 'profit percents: ' + str(report[key]['profit_percents']) + '\n'
            dollar_info = 'profit dollars: ' + str(report[key]['profit_value']) + '\n'
            orders_info = 'orders: ' + '\n' + str(report[key]['orders']) + '\n' + '\n'
            coeffs_info = 'coeffs: ' + '\n' + str(report[key]['coeffs']) + '\n'
            report_text = time_info + cycle_info + percent_info + dollar_info + orders_info + coeffs_info
            bot.send_message(chat_id=job.context['chat_id'], text= report_text)
    pool.close()
            
if __name__ == '__main__':
    def state(bot, update):
        try:
            do_main(bot, None)
            update.message.reply_text('Ищу заебал!')
        except:
            update.message.reply_text('Хуйня какая-то')

    def stop(bot, update, chat_data):
        logger = logging.getLogger("TelegramApp.stop")
        try:
            if 'job' not in chat_data:
                update.message.reply_text('Not active')
                logger.info('Not active')
                return

            for job in chat_data['job']:
                logger.info('Stopped chat_id:{}'.format(job.context['chat_id']))
                job.schedule_removal()

            del chat_data['job']

            update.message.reply_text('Stopped!')
        except Exception as e:
            # print(e)
            logger.error(e)


    def hello(bot, update):
        update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))


    def balance(bot, update):
        kraken = ccxt.kraken({
            'apiKey': '-',
            'secret': '-',})
        usd = kraken.fetch_balance()['USD']['free']
        print(usd)
        update.message.reply_text(str(usd))
          
    def start(bot, update, job_queue, chat_data):
        logger = logging.getLogger("TelegramApp.start")
        try:
            if 'job' in chat_data:
                update.message.reply_text('Already started')
                logger.info('Already started')
                return
            # job1 = job_queue.run_repeating(do_job, 1, context={'chat_id':update.message.chat_id, 'chat_data': chat_data})
            # time.sleep(1)
            job2 = job_queue.run_repeating(do_main, 3.0, context={'chat_id': update.message.chat_id,
                                                                'chat_data': chat_data})
            logger.info('Scheduled chat_id: {}'.format(update.message.chat_id))

            chat_data['job'] = [job2]
            chat_data['values'] = []
        except Exception as e:
            # print(e)
            logger.error(e)


    with ThreadPool(processes=3) as pool:
        updater = Updater('!!!', workers=1)

        updater.dispatcher.add_handler(CommandHandler('start', start, pass_job_queue=True,
                                                      pass_chat_data=True))
        updater.dispatcher.add_handler(CommandHandler('stop', stop, pass_chat_data=True))
        updater.dispatcher.add_handler(CommandHandler('state', state))
        updater.dispatcher.add_handler(CommandHandler('hello', hello))
        updater.dispatcher.add_handler(CommandHandler('balance', balance))

        updater.start_polling()
        updater.idle()
