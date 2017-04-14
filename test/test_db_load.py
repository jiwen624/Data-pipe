"unittest"

import unittest
import psycopg2
from unittest import mock
from db_load import IronMQFile, load_data_to_postgre
from main import event_handlers, mq
from settings import settings


class TestIronMQFile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read(self):
        mq = IronMQFile(None)
        mq.readline = mock.Mock(return_value='hello\n')
        self.assertEqual(mq.read(3), 'hel')
        self.assertEqual(mq.leftover, 'lo\n')
        self.assertEqual(mq.read(5), 'lo\nhe')
        self.assertEqual(mq.leftover, 'llo\n')
        self.assertEqual(mq.read(12), 'llo\nhello\nhe')
        self.assertEqual(mq.leftover, 'llo\n')
        self.assertEqual(mq.read(11), 'llo\nhello\nh')
        self.assertEqual(mq.read(1), 'e')
        self.assertEqual(mq.leftover, 'llo\n')
        self.assertEqual(mq.read(0), '')
        self.assertEqual(mq.leftover, 'llo\n')

    def test_readline(self):
        mq = IronMQFile(None)
        mq._populate_cache = mock.Mock(return_value=None)
        mq.event_cache = ['hello', 'world']
        self.assertEqual(mq.readline(), 'hello\n')
        self.assertEqual(mq.readline(), 'world\n')
        self.assertEqual(mq.readline(), '')

    # Generally for a unit test I should use a stub for db connections and cursors here.
    # However, as the main function of this method is to execute db operations
    # and the logic of itself is very simple, it seems to be useless to just test
    # it with stubs. Instead, let's treat it as half unittest and half integration test
    # to try corner cases to raise and handle exceptions.
    # TODO: split the function to separate parts: external connections and the logic.
    # TODO: there should be more test cases to increase the coverage.
    def test_load_data_to_postgre(self):
        db_parms = { #'dbname': None,
                    'user': settings.DB_USER,
                    'password': settings.DB_PASSWORD,
                    'host': '127.0.0.1',
                    'port': '12345'
                    }
        tbl_quefile_dict = {}

        for tbl_name in event_handlers.handlers.keys():
            tbl_quefile_dict[tbl_name] = IronMQFile(mq.queue(tbl_name))

        self.assertEqual(load_data_to_postgre(None, db_parms, 'test'), None)
