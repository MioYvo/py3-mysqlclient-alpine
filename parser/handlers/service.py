# coding=utf-8
# __author__ = 'Mio'
import json

from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from schema import Schema, Use, Optional
from tornado.log import app_log

from parser.settings import CONNECT_TIMEOUT, CHARSET
from parser.utils.gtornado.web import BaseRequestHandler
from parser.utils.json_encoder import MySQLQueryEncoder
from parser.utils.tracking_column import get_tracking_column, set_last_row, TypeNotFoundException, \
    NotPickleLoadException, clear_last_row


class FetchDataHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        """Secure fetch data by using MySQL parser-service.
        """
        data = self.post_schema()
        if data is False:
            return

        if data['clear_run'] is True:
            clear_last_row(data['type'])

        if data['tracking_column'] and data['tracking_column_type']:
            try:
                tracking_column = get_tracking_column(data['type'],
                                                      data['tracking_column'],
                                                      data['tracking_column_type'])
            except TypeNotFoundException as e:
                self.write_parse_args_failed_response(e.message)
                return
            except NotPickleLoadException as e:
                self.write_parse_args_failed_response(e.message)
                return

            data['sql'] = data['sql'].format(tracking_column=tracking_column)

        try:
            db = connect(
                host=data['host'], port=data['port'], user=data['user'],
                password=data['password'], database=data['database'],
                connect_timeout=CONNECT_TIMEOUT, charset=CHARSET,
                cursorclass=DictCursor
            )
            cur = db.cursor()
            cur.execute(data['sql'])
            result = cur.fetchall()
            cur.close()
            db.close()
        except Exception as e:
            self.write_error_response(message="sql error", content=e.args)
            return
        else:
            set_last_row(data['type'], result[-1] if result else None)
            secure_result = dict(error_code=0, message="", content=result)
            result_dumped = json.dumps(secure_result, cls=MySQLQueryEncoder)
            # self.write_response(content=result)
            self.set_header("Content-Type", "application/json;charset=UTF-8")
            self.write(result_dumped)
            return

    def post_schema(self):
        try:
            data = Schema({
                "host": Use(str),
                Optional("port", default=3306): Use(int),
                "user": Use(str),
                "password": Use(str),
                "database": Use(str),
                "sql": Use(str),
                "type": Use(str),
                Optional("tracking_column", default=None): Use(str),
                Optional("tracking_column_type", default=None): Use(str),
                Optional("clear_run", default=False): Use(bool)
            }).validate(self.get_body_args())
        except Exception as e:
            app_log.error(e)
            self.write_parse_args_failed_response(content=e.args)
            return False
        else:
            return data
