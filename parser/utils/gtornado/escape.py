#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-09-07 15:19:48
# @Author  : Jim Zhang (jim.zoumo@gmail.com)
# @Github  : https://github.com/zoumo

import re
from schema import And, Use, Or
from tornado.escape import utf8


def power_split(value, separator=',', schema=str):
    assert callable(schema)
    value = utf8(value)
    value = value.strip()
    l = re.split("\s*"+separator+"\s*", value)  # 这个slip直接去除逗号左右的空格
    return [v for v in l if v != '']


schema_utf8 = And(Or(Use(utf8), Use(str)), len)
schema_int = Use(int)
schema_float = Use(float)
schema_objectid = And(schema_utf8, lambda x: len(x) == 24)
