""" -- The Exceptions.
    - data pipeline project
    - author: eric yang
    - date: mar 31, 2017
"""

"""Error code definitions"""
RET_OK = 0
ERR_BASE_EVENT_EXCEPTION = 1
ERR_NO_CONTENT_EXCEPTION = 2
ERR_BAD_JSON_STRUCTURE = 3
ERR_KEY_MISSING_EXCEPTION = 4
ERR_VAL_TYPE_EXCEPTION = 5
ERR_INPUT_TOO_LONG = 6
ERR_UNSUPPORTED_EVENT = 7
ERR_INTERNAL_ERR = 100

"""Error message definitions"""
MSG_RET_OK = ''
MSG_BASE_EVENT_EXCEPTION = 'Unidentified general event error'
MSG_NO_CONTENT_EXCEPTION = 'No message content found'
MSG_BAD_JSON_STRUCTURE = 'Bad json structure'
MSG_KEY_MISSING_EXCEPTION = 'mandatory key missing'
MSG_VAL_TYPE_EXCEPTION = 'invalid value type'
MSG_INTERNAL_ERR = 'internal error'
MSG_INPUT_TOO_LONG = 'input too long or too short'
MSG_UNSUPPORTED_EVENT = 'unsupported event'


class EventException(Exception):
    errno = ERR_BASE_EVENT_EXCEPTION
    msg = MSG_BASE_EVENT_EXCEPTION

    def __init__(self, key=None):
        self.key = key


class NoContentException(EventException):
    errno = ERR_NO_CONTENT_EXCEPTION
    msg = MSG_NO_CONTENT_EXCEPTION


class BadJsonStructureException(EventException):
    errno = ERR_BAD_JSON_STRUCTURE
    msg = MSG_BAD_JSON_STRUCTURE


class KeyMissingException(EventException):
    errno = ERR_KEY_MISSING_EXCEPTION
    msg = MSG_KEY_MISSING_EXCEPTION


class ValueTypeErrException(EventException):
    errno = ERR_VAL_TYPE_EXCEPTION
    msg = MSG_VAL_TYPE_EXCEPTION


class InputExceedLimitException(EventException):
    errno = ERR_INPUT_TOO_LONG
    msg = MSG_INPUT_TOO_LONG


class UnsupportedEventException(EventException):
    errno = ERR_UNSUPPORTED_EVENT
    msg = MSG_UNSUPPORTED_EVENT


class PushMQException(EventException):
    errno = ERR_INTERNAL_ERR
    msg = MSG_INTERNAL_ERR
