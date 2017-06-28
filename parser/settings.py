# coding=utf-8
# __author__ = 'Mio'
from redis import Redis

# --------------------     redis    --------------------
r = Redis(host="127.0.0.1")

# --------------------    MySQLdb   --------------------
CONNECT_TIMEOUT = 3
CHARSET = "utf8"

# --------------------    tornado   --------------------
settings = {
    "debug": True,
    "autoreload": True,
}
