import logging
import string
from collections.abc import Iterable

def write(deq, filename='log.txt'):
    logging.basicConfig(filename=filename, level=logging.ERROR,  format='%(asctime)s %(message)s')
    if deq[-1] is None:
        deq.pop()
    for e in deq:
        message = ' '.join(map(str, e)) if isinstance(e, Iterable)  else str(e)
        logging.error(message)
