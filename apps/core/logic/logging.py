from contextlib import contextmanager
from time import time

from django.db import connection


@contextmanager
def query_counter(logger=None):
    start = time()
    queries_start = len(connection.queries)
    message = "  -- start --"
    if logger:
        logger.debug(message)
    else:
        print(message)
    try:
        yield
    finally:
        message = "  -- end: duration: {:.2f} s, db queries: {} --".format(
            time() - start, len(connection.queries) - queries_start
        )
        if logger:
            logger.debug(message)
        else:
            print(message)
