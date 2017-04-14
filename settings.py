"""
    The default configurations (or conventions) in this file can be overrided by
    either /etc/datapipe.json or the path of environment variable $datapipe_CNF, if defined.
    - from the data pipeline project
    - author: eric yang
    - date: mar 31, 2017
"""

import json
import os


class _Settings:
    """Here is the default configuration, change the default values with
    /etc/datapipe.json or the path specified with datapipe_CNF"""
    def __init__(self):
        self.DEFAULT_APP_PORT = 8080
        # The maximum length of user input, strings longer than this will be
        # rejected.
        self.INPUT_MAX_LEN = 2048
        # The coding scheme
        self.ENCODING_SCHEME = 'utf-8'

        # The message queue name and project id
        self.MQ_HOST = 'mq-aws-eu-west-1-1.iron.io'
        self.MQ_PROJECT_ID = '58de57f452c4150006d9bf2a'
        self.MQ_TOKEN = 'Q2R1DT0dV7bF6esxAT1c'
        self.MQ_FETCH_MSG_NUM = 100

        self.DB_LOAD_INTERVAL = 300
        self.DB_LOAD_MIN_INTERVAL = 10
        self.DB_LOAD_WORKER = 3
        self.DB_LOAD_CHUNK_SIZE = 524288
        self.DB_NAME = 'test'
        self.DB_USER = 'test'
        self.DB_PASSWORD = 'testpwd'
        self.DB_HOST = 'datapipe.test.com'
        self.DB_PORT = 5432


def _merge_settings(_settings, cnf_json):
    """Merge the items of Settings instance and user-defined configurations"""
    for key in cnf_json:
        key = key.upper()
        if (hasattr(_settings, key)
            and isinstance(cnf_json[key], type(getattr(_settings, key)))):
            setattr(_settings, key, cnf_json[key])
    return _settings


def get_merged_settings():
    """Get the merged config instance"""
    _settings = _Settings()

    cnf = os.environ.get('DATAPIPE_CNF', '/etc/datapipe.json')
    if not os.path.isfile(cnf):
        return _settings

    with open(cnf) as cnf_file:
        # It may throw a JsonDecodeError but we don't catch it
        # as we cannot do anything with it.
        cnf_json = json.load(cnf_file)
        return _merge_settings(_settings, cnf_json)


settings = get_merged_settings()
