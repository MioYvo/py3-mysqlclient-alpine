# coding=utf-8
# __author__ = 'Mio'
"""
Mysql parser
"""
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.log import app_log
from tornado.options import define, options

from parser.urls import urls
from parser.settings import settings


define("port", default=6464, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, urls, **settings)


if __name__ == "__main__":
    options.parse_command_line()
    application = Application()
    server = tornado.httpserver.HTTPServer(application, xheaders=True)
    server.listen(options.port)
    app_log.info("run on port:{}".format(options.port))
    io_loop_ = tornado.ioloop.IOLoop.current()
    io_loop_.start()
