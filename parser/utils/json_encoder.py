# coding=utf-8
# __author__ = 'Mio'

import json
from decimal import Decimal
from datetime import datetime, date, timedelta

from tornado.escape import native_str

from .gtz import datetime_2_string


class MySQLQueryEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return native_str(obj)
        if isinstance(obj, (datetime, date)):
            return datetime_2_string(obj)
        if isinstance(obj, timedelta):
            return (datetime.min + obj).time().isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
