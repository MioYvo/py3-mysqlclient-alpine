#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-11-05 11:18:24
# @Author  : Jim Zhang (jim.zoumo@gmail.com)
# @Github  : https://github.com/zoumo

# ========================
# 通用
# ========================

# 未知错误
ERR_UNKNOWN = 4000

# 跟时间相关的错误
ERR_TIME = 4001

# 参数解析错误
ERR_ARG = 4002

# 无法根据id或者sign找到对应的实例
ERR_NO_CONTENT = 4004

# 跟钱有关的错误
ERR_MONEY = 4005

# 运力不足
ERR_NO_COURIER = 4006

# 查询单个结果, 返回了多个
ERR_MULTIPLE_OBJ_RETURNED = 4007

# =========================
# 专用
# =========================

# 预约驻派, 保证金相关错误
ERR_DEPOSIT = 41001

# 批量发货
# 重复的快递单号
ERR_EXPR_DUPLICATE_ID = 42001

# 电商发货
ERR_NEED_CONFIRM = 43001
