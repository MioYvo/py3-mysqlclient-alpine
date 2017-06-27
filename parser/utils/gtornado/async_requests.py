# coding=utf-8

import json
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.log import app_log


class JsonRequest(HTTPRequest):
    def __init__(self, url, method="POST", headers=None, body=None, **kwargs):
        if headers is None:
            headers = {}
        headers['Content-Type'] = "application/json"
        if kwargs is None:
            kwargs = {}
        kwargs.setdefault('request_timeout', 5)
        kwargs.setdefault('connect_timeout', 5)
        super(JsonRequest, self).__init__(url, method=method, headers=headers, body=body, **kwargs)


class NoDataRequest(HTTPRequest):
    def __init__(self, url, method="GET", params=None, **kwargs):
        url = url_concat(url, params)
        if kwargs is None:
            kwargs = {}
        kwargs.setdefault('request_timeout', 5)
        kwargs.setdefault('connect_timeout', 5)
        super(NoDataRequest, self).__init__(url, method=method, **kwargs)


def fetch(request, callback=None, raise_error=False):
    # AsyncHTTPClient 与 IOLoop.current() 挂钩, 默认是从缓存里面拿
    # 如果在此之前有人调用过AsyncHTTPClient的话, 则max_clients会是10
    http_client = AsyncHTTPClient(max_clients=100)
    if http_client.max_clients < 100:
        http_client = AsyncHTTPClient(force_instance=True, max_clients=100)

    app_log.info("[async_requests] method[%s], url[%s], data[%s]", request.method, request.url, request.body)

    return http_client.fetch(request, callback=callback, raise_error=raise_error)


def session(method, url, callback=None, data=None, raise_error=False, **kwargs):
    if data is None:
        request = NoDataRequest(url, method=method, **kwargs)
    else:
        request = JsonRequest(url, method=method, body=json.dumps(data), **kwargs)
    # AsyncHTTPClient 与 IOLoop.current() 挂钩, 默认是从缓存里面拿
    # 如果在此之前有人调用过AsyncHTTPClient的话, 则max_clients会是10
    # http_client = AsyncHTTPClient(max_clients=100)
    # if http_client.max_clients < 100:
    #     http_client = AsyncHTTPClient(force_instance=True, max_clients=100)
    #
    # logging.info("[async_requests] method[%s], url[%s], data[%s]", method, url, data)
    # return http_client.fetch(request, callback=callback, raise_error=raise_error)

    return fetch(request, callback=callback)


def get(url, params=None, callback=None, **kwargs):
    url = url_concat(url, params)
    return session("GET", url, callback=None, **kwargs)


def post(url, data=None, callback=None, **kwargs):
    return session("POST", url, callback=None, data=data, **kwargs)


def patch(url, data=None, callback=None, **kwargs):
    return session("PATCH", url, callback=None, data=data, **kwargs)


def put(url, data=None, callback=None, **kwargs):
    return session("PUT", url, callback=None, data=data, **kwargs)


def delete(url, params=None, callback=None, **kwargs):
    url = url_concat(url, params)
    return session("DELETE", url, callback=None, **kwargs)


def head(url, callback=None, **kwargs):
    return session("HEAD", url, callback=None, **kwargs)
