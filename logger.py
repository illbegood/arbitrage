import logging
from collections.abc import Iterable

def write(deq, filename='log'):
    logging.basicConfig(filename=filename, level=logging.ERROR, format='%(message)s')
#    message = ' '.join(map(str, deq)) + '\n'
#    logging.error(message)
    for e in deq:
        message = ' '.join(e) if isinstance(e, Iterable)  else str(e)
        logging.error(message)
