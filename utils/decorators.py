import functools
import logging

import psycopg2
from psycopg2.extras import DictCursor

logger = logging.getLogger("CovIS-Database")


def use_cursor(func):
    @functools.wraps(func)
    def wrapper_use_cursor(self, *args, **kwargs):
        try:
            connection = getattr(self, "connection")
            cursor = connection.cursor(cursor_factory=DictCursor)
            return func(self, *args, **kwargs, cursor=cursor)

        except (Exception, psycopg2.Error) as error:
            if connection:
                logger.error(f"Function {func.__name__} call failed")
                logger.error(error)

        finally:
            if connection:
                cursor.close()

    return wrapper_use_cursor
