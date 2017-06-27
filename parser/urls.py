# coding=utf-8
# __author__ = 'Mio'
from parser.handlers import service

urls = [
    (r"^/data$", service.FetchDataHandler),
]
