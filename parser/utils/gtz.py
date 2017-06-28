# coding=utf-8
# __author__ = 'Mio'
from datetime import datetime
import dateutil.parser

UTC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
UTC_MONTH_FORMAT = '%Y-%m'


def string_2_datetime(_string, _format=UTC_DATETIME_FORMAT):
    if isinstance(_string, bytes):
        _string = _string.decode()
    return datetime.strptime(_string, _format)


def datetime_2_string(_datetime, _format=UTC_DATETIME_FORMAT):
    return _datetime.strftime(_format)


def isoformat_2_time(_isoformat_str):
    d = dateutil.parser.parse(_isoformat_str)
    return d.time()
