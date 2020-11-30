import logging

#def process_cycle(log):
#    logging.debug('Total balance: '+  log['balance'])
#   logging.debug('Trade balance:' + log['trade_balance'])
#   for symb, (order_value, price)

def write(deque, filename='log'):
    logging.basicConfig(filename=filename, encoding='utf-8', level=logging.DEBUG)
    map(print, deque)
