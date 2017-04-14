""" This file contains the processing of unloading data from message queue
    and loading data to the database by \COPY FROM.
    An file-like class (IronMQFile) is implemented as a wrapper to the IronMQ
    and provides the file operations interface (read() and readline()).
    The psycopg2.copy_from() implements the \copy interface of PostgreSQL
    which accepts a file object. So basically the data flow is extracting data
    from the message queue (with the help of the file wrapper) and load it to
    the database.
    - data pipeline project
    - author: eric yang
    - date: mar 31, 2017
"""
import psycopg2
import time
import logging
import sys
from settings import settings

log = logging.getLogger(__file__)


class IronMQFile:
    """A file-like wrapper for IronMQ, which will act as a input to the COPY FROM
        command."""
    def __init__(self, queue):
        self.queue = queue
        self.event_cache = list()
        self.leftover = None

    def _populate_cache(self):
        """Try to fetch as many of rows as possible, therefore we need a cache."""
        msgs_json = self.queue.reserve(max=settings.MQ_FETCH_MSG_NUM, delete=True)
        if not (msgs_json and isinstance(msgs_json, dict)):
            return

        for msg in msgs_json.get('messages', []):
            event = msg.get('body', None)
            if event:
                self.event_cache.append(event)

    def read(self, size=-1):
        """Read data with a chunk size"""
        ret = []
        size_left = size if size >= 0 else sys.maxsize

        if self.leftover:
            if len(self.leftover) <= size_left:
                ret.append(self.leftover)
                size_left -= len(self.leftover)
                self.leftover = None
            else:
                ret.append(self.leftover[:size_left])
                self.leftover = self.leftover[size_left:]
                size_left = 0

        while size_left > 0:
            line = self.readline()
            if not line:
                break

            len_line = len(line)
            if size_left >= len_line:
                ret.append(line)
            else:
                ret.append(line[:size_left])
                self.leftover = line[size_left:]
            if size == -1:
                size_left = sys.maxsize
            else:
                size_left -= len_line

        return ''.join(ret) if ret else ''

    def readline(self, size=-1):
        """TODO: size parameter is not supported right now as
            copy_from does not use it"""
        ret = []

        if size == -1:
            if len(self.event_cache) == 0:
                self._populate_cache()

            if self.event_cache:
                next_event = self.event_cache.pop(0)
                if next_event:
                    ret.append(next_event)

            if ret:
                ret.append('')
                ret_str = '\n'.join(ret)
            else:
                ret_str = ''

            return ret_str
        else:
            raise NotImplemented


def load_data_to_postgre(queue_file, db_parms, tbl_name):
    """This function extract from the data source and load the data
        to the backend database in a pre-configured interval."""
    if not (queue_file and db_parms and tbl_name):
        return

    conn = None

    while True:
        curr_time = time.time()

        try:
            conn = psycopg2.connect(**db_parms)

            curs = conn.cursor()
            # The psycopg2 interface for \copy command
            curs.copy_from(queue_file, tbl_name, sep=',', size=settings.DB_LOAD_CHUNK_SIZE)

            curs.close()
            conn.commit()
        except psycopg2.DataError:
            conn.rollback()

        except (psycopg2.InternalError,
                psycopg2.DatabaseError,
                psycopg2.OperationalError,
                psycopg2.InterfaceError) as e:
            log.warning(e)

        try:
            if conn:
                conn.close()
        except psycopg2.InterfaceError:
            pass

        next_wakeup_time = settings.DB_LOAD_INTERVAL - time.time() + curr_time
        sleep_time = max(next_wakeup_time, settings.DB_LOAD_MIN_INTERVAL)
        time.sleep(sleep_time)
