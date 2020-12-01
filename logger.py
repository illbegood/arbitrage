import logging
from collections.abc import Iterable

#def process_cycle(log):
#    logging.debug('Total balance: '+  log['balance'])
#   logging.debug('Trade balance:' + log['trade_balance'])
#   for symb, (order_value, price)

def write(deq, filename='log'):
    logging.basicConfig(filename=filename, level=logging.DEBUG, format='%(message)s')
    for e in deq:
        if isinstance(e, Iterable):
            #map(print, deq)
            for i in e:
                logging.debug(i)
        else:
            print(e)
