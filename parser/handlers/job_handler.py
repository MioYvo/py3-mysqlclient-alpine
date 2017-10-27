# coding=utf-8
# __author__ = 'Mio'
import json

from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from tornado.log import app_log

from parser.settings import scheduler, TRACKING_JOBS
from parser.utils.json_encoder import MySQLQueryEncoder
from parser.utils.rabbit_publisher import raw_data_pubber
from parser.utils.tracking_column import (clear_last_row, get_tracking_column, set_last_row,
                                          TypeNotFoundException, NotPickleLoadException)
from parser.settings import (MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD,
                             MYSQL_CONNECT_TIMEOUT, MYSQL_CONNECT_CHARSET)


def tracking_func(sql, data_type, tracking_column, tracking_column_type, clear_run=False,
                  host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER,
                  password=MYSQL_PASSWORD):
    if clear_run is True:
        clear_last_row(data_type)

    try:
        tracking_column = get_tracking_column(data_type,
                                              tracking_column,
                                              tracking_column_type)
    except TypeNotFoundException as e:
        app_log.error(e.args)
        return
    except NotPickleLoadException as e:
        app_log.error(e.args)
        return
    else:
        full_sql = sql.format(tracking_column=tracking_column)

    try:
        db = connect(
            host=host, port=port, user=user,
            password=password, database=database,
            connect_timeout=MYSQL_CONNECT_TIMEOUT, charset=MYSQL_CONNECT_CHARSET,
            cursorclass=DictCursor
        )
        cur = db.cursor()
        cur.execute(full_sql)
        result = cur.fetchall()
        cur.close()
        db.close()
    except Exception as e:
        app_log.error("sql error: {}".format(e.args))
        return
    else:
        set_last_row(data_type, result[-1] if result else None)
        secure_result = dict(error_code=0, message="", content=result)
        result_dumped = json.dumps(secure_result, cls=MySQLQueryEncoder)
        # self.write_response(content=result)
        raw_data_pubber.publish_message(result_dumped)


def load_jobs_from_env():
    """
    TRACKING_JOBS_PRELOAD
    [
        {
            "trigger": "cron",
            "func_kwargs": {},
            "cron_kwargs": {}
        }
    ]
    :return:
    """
    tracking_jobs_list = json.loads(TRACKING_JOBS)
    for job in tracking_jobs_list:
        # TODO check duplicate job
        scheduler.add_job(tracking_func, trigger=job['trigger'],
                          kwargs=job['func_kwargs'], **job['cron_kwargs'])
