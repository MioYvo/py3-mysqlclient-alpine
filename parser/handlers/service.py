# coding=utf-8
# __author__ = 'Mio'
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from schema import Schema, Use, Optional
from tornado.log import app_log

from parser.settings import CONNECT_TIMEOUT, CHARSET
from parser.utils.gtornado.web import BaseRequestHandler
from parser.utils import y_pickle


class FetchDataHandler(BaseRequestHandler):
    def post(self):
        data = self.post_schema()
        if data is False:
            return

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
            # for row_dict in result:
            #     for key in row_dict:
            #         if isinstance(row_dict[key], bytes):
            #             row_dict[key] = row_dict[key].decode()
            #         if isinstance(row_dict[key], datetime):
            #             row_dict[key] = datetime_2_string(row_dict[key])
            import base64

            result = y_pickle.encode(result)
            self.write_response(content=result)
            return

    def post_schema(self):
        try:
            # TODO 字段和值都需要加密
            data = Schema({
                "host": Use(str),
                Optional("port", default=3306): Use(int),
                "user": Use(str),
                "password": Use(str),
                "database": Use(str),
                "sql": Use(str)
            }).validate(self.get_body_args())
        except Exception as e:
            app_log.error(e)
            self.write_parse_args_failed_response(content=e.args)
            return False
        else:
            return data
