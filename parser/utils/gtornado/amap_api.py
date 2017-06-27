# coding=utf-8
# __author__ = 'mio'
# import requests
import random
import ujson
from tornado import gen, httpclient
# from tornado.log import app_log
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.httputil import url_concat  # GET方法组装参数
from tornado.log import app_log

amap_walking_url = "http://restapi.amap.com/v3/direction/walking"
amap_geocode_url = "http://restapi.amap.com/v3/geocode/geo"

key_list = [
    "538e250d2741dc084117c0dff1673272",  # mio
    "c2da11a4537c64e2ef4233ba919cfcbd"  # 风先生普通
]


@gen.coroutine
def amap_get_distance(from_lng, from_lat, to_lng, to_lat):
    """
    高德地图获取步行距离
    :param from_lng:
    :param from_lat:
    :param to_lng:
    :param to_lat:
    :return:
    """
    params = dict(
        origin=",".join((str(from_lng), str(from_lat))),
        destination=",".join((str(to_lng), str(to_lat))),
        key=random.choice(key_list)
    )
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(
            HTTPRequest(url=url_concat(amap_walking_url, params), method="GET", request_timeout=0.5))
        response = ujson.loads(response.body)
        distance = int(response['route']['paths'][0]['distance'])
    except HTTPError:
        app_log.info("***___!!!__*** Amap Walking Distance Cal Timeout ***___!!!__***")
        raise gen.Return((0, "timeout"))
    except Exception:
        app_log.info("***___!!!__*** Amap Walking Distance Cal Exception ***___!!!__***")
        raise gen.Return((0, "exception"))
    else:
        raise gen.Return((distance, "ok"))


@gen.coroutine
def amap_geocode(address):
    """
    高德地图，通过地址解析经纬度
    :param address:
    :return: return latitude, longitude
    """
    params = dict(
        address=address,
        output="json",
        key=random.choice(key_list)
    )
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(
            HTTPRequest(url=url_concat(amap_geocode_url, params), method="GET", request_timeout=0.5))
        response = ujson.loads(response.body)
        lat, lng = response['geocodes'][0]['location'].split(',')[::-1]
    except HTTPError:
        app_log.error("***___!!!__*** Amap Geocode Timeout ***___!!!__***")
        return [None, None]
    except Exception as e:
        app_log.error("***___!!!__*** Amap Geocode Failed {}***___!!!__***".format(e))
        return [None, None]
    else:
        return [lng, lat]
