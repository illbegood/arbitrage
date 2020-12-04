import logging
from collections.abc import Iterable

def write(deq, filename='log'):
    logging.basicConfig(filename=filename, level=logging.ERROR, format='%(message)s')
    message = ' '.join(map(str, deq)) + '\n'
    logging.error(message)
    #for e in deq:
        #if isinstance(e, Iterable):
            #map(print, deq)
            #logging.error(str(e))
            #for i in e:
                #logging.debug(i)
        #else:
            #print(e)
