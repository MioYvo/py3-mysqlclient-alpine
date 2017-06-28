# coding=utf-8
# __author__ = 'Mio'
import pickle

from tornado.log import app_log

from parser.settings import r
from parser.utils.gtz import datetime_2_string, SQL_DATETIME_FORMAT
from datetime import datetime

class TypeNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class NotPickleLoadException(Exception):
    def __init__(self, message):
        self.message = message

STARTING_TYPE_MAP = {
    "timestamp": datetime.fromtimestamp(0),
    "id": 0,
}


def get_tracking_column(_type, tracking_column, tracking_column_type):
    rst = r.get(_type)
    if not rst:
        app_log.warning("not found {}".format(_type))
        return STARTING_TYPE_MAP.get(tracking_column_type)

    _rst = pickle.loads(rst)
    if not _rst:
        app_log.warning("cannot pickle loads type:{}".format(_type))
        return STARTING_TYPE_MAP.get(tracking_column_type)

    tc = _rst.get(tracking_column)
    if tracking_column_type is 'timestamp':
        return datetime_2_string(tc, SQL_DATETIME_FORMAT)
    else:
        return tc


def set_last_row(_type, last_row):
    if last_row:
        return r.set(name=_type, value=pickle.dumps(last_row))
    else:
        return False


def clear_last_row(_type):
    return r.delete(_type)
