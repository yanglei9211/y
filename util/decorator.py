#!/usr/bin/env python
# encoding=utf-8
import time
from functools import wraps


def show_time_cost(tar_func):
    @wraps(tar_func)
    def wrap_func(*args, **kwargs):
        st = time.time()
        res = tar_func(*args, **kwargs)
        print "%s cost %f ms" % (tar_func.__name__, time.time() - st)
        return res
    return wrap_func
