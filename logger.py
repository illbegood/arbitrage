import logging
import string
from collections.abc import Iterable

def write(deq, filename='log'):
    logging.basicConfig(filename=filename, level=logging.ERROR, format='%(asctime)s %(message)s')
    for e in deq:
        message = ' '.join(map(str, e)) if isinstance(e, Iterable)  else str(e)
        logging.error(message)
