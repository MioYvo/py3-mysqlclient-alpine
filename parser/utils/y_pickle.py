# coding=utf-8
# __author__ = 'Mio'
from base64 import b64decode, b64encode
from pickle import loads, dumps
from zlib import decompress, compress


def encode(value, compress_object=False):
    value = dumps(value)
    if compress_object:
        value = compress(value)
    value = b64encode(value)
    return value.decode()  # decode bytes to str


def decode(value, compress_object=False):
    value = value.encode()  # encode str to bytes
    value = b64decode(value)
    if compress_object:
        value = decompress(value)
    return loads(value)
