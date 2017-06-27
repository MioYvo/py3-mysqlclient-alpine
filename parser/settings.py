# coding=utf-8
# __author__ = 'Mio'
from redis import Redis

# --------------------     redis    --------------------
r = Redis("redis")

# --------------------    MySQLdb   --------------------
CONNECT_TIMEOUT = 3
CHARSET = "utf8"

# --------------------    tornado   --------------------
settings = {
    "debug": True,
    "autoreload": True,
}
