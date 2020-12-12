import logging
import string
from collections.abc import Iterable

def write(deq, filename='log'):
    logging.basicConfig(filename=filename, level=logging.NOTSET,  format='%(asctime)s %(message)s')
    if deq[-1] is None:
        deq.pop()
    for e in deq:
        message = ' '.join(map(str, e)) if isinstance(e, Iterable)  else str(e)
        logging.info(message)
