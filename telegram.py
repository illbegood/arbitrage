import ccxt
import networkx as nx
import logging
import logging.config
import logging.handlers
from multiprocessing.pool import ThreadPool
import multiprocessing

from telegram.ext import Updater, CommandHandler
import fetch
import bellman_ford
import optimize
import trade


def do_main(bot, job):
    binance = ccxt.binance({
    'apiKey': '!',
    'secret': '!', })
    logger = logging.getLogger("TelegramApp.do_main")
    start_time = time.time()
    exch_dict = {'binance': binance} #'huobi': huobi}
    nodes, edges = fetch_exchange('binance', binance)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    depth = 10
    start_with = 'BTC.binance'
    paths = bellman_ford(G, start_with)
    args = [[G, path, depth] for path in paths]
    pool = multiprocessing.Pool(processes=6)
    report = {}
    for res in pool.imap_unordered(opt_parallel, args):
        if res is None:
            continue
        else:
            profit_value, profit_percents, prob, trade_args, cycle, usdt_balance = res
            #bot.send_message(chat_id=job.context['chat_id'], text='cycle found')
            #bot.send_message(chat_id=job.context['chat_id'], text=str(100 * profit_value / profit_percents))
            if (100 * profit_value / profit_percents > 0.8 * usdt_balance):
                try:
                    trade(cycle, trade_args, G)
                    bot.send_message(chat_id=job.context['chat_id'], text='trade succeeded')
                except:
                    bot.send_message(chat_id=job.context['chat_id'], text='trade failed')
                report[str(cycle)] = {'balance': usdt_balance, 'profit_percents': profit_percents, 'profit_value': profit_value, 'orders, coeffs': trade_args}
                #trade(cycle, trade_args[0], trade_args[1], G, exch_dict)
    end_time = time.time() - start_time
    if (len(report) > 0):
        for key in report.keys():
            time_info = 'processing time: ' + str(end_time) + '\n'
            cycle_info = key + '\n'
            balance_info = 'balance: ' + str(report[key]['balance']) + '\n'
            percent_info = 'profit percents: ' + str(report[key]['profit_percents']) + '\n'
            dollar_info = 'profit dollars: ' + str(report[key]['profit_value']) + '\n'
            orders_info = 'orders, coeffs: ' + '\n' + str(report[key]['orders, coeffs']) + '\n' + '\n'
            report_text = time_info + balance_info + cycle_info + percent_info + dollar_info + orders_info
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
        binance = ccxt.binance({
        'apiKey': '-',
        'secret': '-', })
        balance_usdt = binance.fetch_balance()['USDT']['free']
        update.message.reply_text(str(balance_usdt))


          
    def start(bot, update, job_queue, chat_data):
            logger = logging.getLogger("TelegramApp.start")
            try:
                if 'job' in chat_data:
                    update.message.reply_text('Already started')
                    logger.info('Already started')
                    return
                # job1 = job_queue.run_repeating(do_job, 1, context={'chat_id':update.message.chat_id, 'chat_data': chat_data})
                # time.sleep(1)
                job2 = job_queue.run_repeating(do_main, 10.0, context={'chat_id': update.message.chat_id,
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
