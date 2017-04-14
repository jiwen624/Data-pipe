"""unittest"""

import unittest
from main import (EventHandlers,
                  CrashReportEvent,
                  PurchaseEvent,
                  InstallEvent,
                  pre_processing,
                  input_processing,
                  get_err_ret,
                  get_ok_ret)
import exceptions


class TestEventHandlers(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_register(self):
        handler = EventHandlers()
        self.assertEqual(handler.register('crash_report', CrashReportEvent),
                         CrashReportEvent)
        self.assertEqual(handler.register('purchase', PurchaseEvent),
                         PurchaseEvent)
        self.assertEqual(handler.register('install', InstallEvent),
                         InstallEvent)
        self.assertEqual(handler.register('', InstallEvent), None)
        self.assertEqual(handler.register('install', None), None)
        self.assertEqual(len(handler.handlers), 3)

    def test_get_handler(self):
        handler = EventHandlers()
        handler.register('crash_report', CrashReportEvent)
        handler.register('purchase', PurchaseEvent)
        handler.register('install', InstallEvent)
        self.assertEqual(handler.get_handler('crash_report'), CrashReportEvent)
        self.assertEqual(handler.get_handler('purchase'), PurchaseEvent)
        self.assertEqual(handler.get_handler('install'), InstallEvent)
        self.assertEqual(handler.get_handler('not_supported'), None)
        self.assertEqual(handler.get_handler(None), None)

    def test_crash_report_event(self):
        crash_report = {"event_name": "crash_report",
                        "user_id": 666,
                        "timestamp": 1000,
                        "message": "TheFirstHeroku"}
        evt = CrashReportEvent(crash_report)
        self.assertEqual(str(evt), '666,1000,TheFirstHeroku')

    def test_crash_report_event_bad_type(self):
        crash_report = {"event_name": "crash_report",
                        "user_id": "666",
                        "timestamp": "1000",
                        "message": "TheFirstHeroku"}
        with self.assertRaises(exceptions.ValueTypeErrException):
            CrashReportEvent(crash_report)

    def test_purchase_event(self):
        purchase = {"event_name": "purchase",
                    "user_id": 666,
                    "timestamp": 1000,
                    "sku": "TheFirstHeroku"}
        evt = PurchaseEvent(purchase)
        self.assertEqual(str(evt), '666,1000,TheFirstHeroku')

    def test_purchase_event_bad_type(self):
        purchase = {"event_name": "purchase",
                        "user_id": "666",
                        "timestamp": "1000",
                        "sku": "TheFirstHeroku"}
        with self.assertRaises(exceptions.ValueTypeErrException):
            PurchaseEvent(purchase)

    def test_install_event(self):
        install = {"event_name": "install",
                   "user_id": 666,
                   "timestamp": 1000}
        evt = InstallEvent(install)
        self.assertEqual(str(evt), '666,1000')

    def test_install_event_bad_type(self):
        install = {"event_name": "install",
                        "timestamp": "1000"}
        with self.assertRaises(exceptions.KeyMissingException):
            InstallEvent(install)

    def test_pre_processing(self):
        with self.assertRaises(exceptions.InputExceedLimitException):
            pre_processing(None)
        with self.assertRaises(exceptions.InputExceedLimitException):
            pre_processing('')
        self.assertEqual(pre_processing(b'12'), 12)
        self.assertEqual(pre_processing(12), 12)
        self.assertEqual('{"event_name": "crash_report"}',
                         '{"event_name": "crash_report"}')
        with self.assertRaises(exceptions.BadJsonStructureException):
            pre_processing('{"event_name')

    def test_input_processing(self):
        with self.assertRaises(exceptions.NoContentException):
            input_processing(None)
        self.assertEqual(input_processing(12),
                         get_err_ret(exceptions.BadJsonStructureException(12)))
        self.assertEqual(input_processing('{"a": "b"}'),
                         get_err_ret(exceptions.KeyMissingException('event_name')))
        self.assertEqual(input_processing('{"event_name": "crash_report__"}'),
                         get_err_ret(exceptions.UnsupportedEventException('crash_report__')))
        ok_msg = '{"event_name": "crash_report","user_id": 666,' \
                 '"timestamp": 1000,"message": "TheFirstHeroku"}'
        self.assertEqual(input_processing(ok_msg), get_ok_ret())


if __name__ == '__main__':
    unittest.main()
