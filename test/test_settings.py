import unittest
from unittest import mock
from unittest.mock import mock_open
import settings


class TestEncrypto(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_merged_settings(self):
        with mock.patch('os.environ.get', return_value='/etc/datapipe.json') as oeg:
            with mock.patch('os.path.isfile', return_value=True) as opi:
                with mock.patch('builtins.open', new_callable=mock_open()) as opn:
                    with mock.patch('json.load'):
                        with mock.patch('settings._merge_settings') as ms:
                            settings.get_merged_settings()
                            oeg.assert_called_with('DATAPIPE_CNF', '/etc/datapipe.json')
                            opi.assert_called_with('/etc/datapipe.json')
                            opn.assert_called_with('/etc/datapipe.json')


    def test_merge_settings_INPUT_MAX_LEN(self):
        new_cnf = settings._merge_settings(settings._Settings(),
                                           {"INPUT_MAX_LEN": 100})
        self.assertEqual(new_cnf.INPUT_MAX_LEN, 100)

    def test_merge_settings_ENCODING_SCHEME(self):
        new_cnf = settings._merge_settings(settings._Settings(),
                                           {"ENCODING_SCHEME": 'utf-8'})
        self.assertEqual(new_cnf.ENCODING_SCHEME, 'utf-8')

    def test_merge_settings_DB_LOAD_INTERVAL(self):
        new_cnf = settings._merge_settings(settings._Settings(),
                                           {"DB_LOAD_INTERVAL": 500})
        self.assertEqual(new_cnf.DB_LOAD_INTERVAL, 500)

    def test_merge_settings_DEFAULT_APP_PORT(self):
        new_cnf = settings._merge_settings(settings._Settings(),
                                           {"DEFAULT_APP_PORT": 9999})
        self.assertEqual(new_cnf.DEFAULT_APP_PORT, 9999)

if __name__ == '__main__':
    unittest.main()
