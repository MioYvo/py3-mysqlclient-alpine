# coding=utf-8
# __author__ = 'Mio'
import os

from pytz import utc
from redis import Redis
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.tornado import TornadoScheduler

# --------------------     redis    --------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
r = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

# --------------------    MySQLdb   --------------------

MYSQL_CONNECT_TIMEOUT = os.getenv("MYSQL_CONNECT_TIMEOUT", 3)
MYSQL_CONNECT_CHARSET = os.getenv("MYSQL_CONNECT_CHARSET", "utf8")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "database")

# --------------------    tornado   --------------------
settings = {
    "debug": True,
    "autoreload": True,
}

# --------------------     rabbit     --------------------
RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbit")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_USER", "guest")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD", "guest")
RABBIT_URL = 'amqp://{user}:{password}@{host}:{port}/%2F'

RABBIT_EXCHANGE = os.getenv("RABBIT_EXCHANGE", "direct_one_exchange")
RABBIT_EXCHANGE_TYPE = os.getenv("RABBIT_EXCHANGE_TYPE", "direct")
RABBIT_PARSED_QUEUE = os.getenv("RABBIT_PARSED_QUEUE", "/parsed_data")
RABBIT_PARSED_ROUTING_KEY = os.getenv("RABBIT_PARSED_ROUTING_KEY", "/parsed_data")

# -------------------- ap scheduler --------------------
DEFAULT_INTERVAL_SECONDS = 30
TRACKING_JOBS = os.getenv("TRACKING_JOBS", "")
job_defaults = {'coalesce': True}
jobstores = {'default': RedisJobStore(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)}
scheduler = TornadoScheduler(
    jobstores=jobstores, job_defaults=job_defaults, timezone=utc
)
