# coding=utf-8
# __author__ = 'Mio'
"""
Mysql parser
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname("__file__"), os.pardir)))
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.log import app_log
from tornado.options import define, options

from parser.urls import urls
from parser.settings import settings, scheduler

define("port", default=80, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        scheduler.start()
        scheduler.add_job()
        tornado.web.Application.__init__(self, urls, **settings)


if __name__ == "__main__":
    options.parse_command_line()
    application = Application()
    server = tornado.httpserver.HTTPServer(application, xheaders=True)
    server.listen(options.port)
    app_log.info("run on port:{}".format(options.port))
    io_loop_ = tornado.ioloop.IOLoop.current()
    io_loop_.start()
