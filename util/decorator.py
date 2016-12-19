#!/usr/bin/env python
# encoding=utf-8
import time
from functools import wraps


def show_time_cost(tar_func):
    @wraps(tar_func)
    def wrap_func(*args, **kwargs):
        st = time.time()
        res = tar_func(*args, **kwargs)
        print "function %s cost %f ms" % (tar_func.__name__, time.time() - st)
        return res
    return wrap_func


def memoize(tar_func):
    memo = {}
    max_size = 100000

    @wraps(tar_func)
    def wrap_func(*args):
        if args in memo:
            return memo[args]
        else:
            if memo.__len__() > max_size:
                memo.clear()
            res = tar_func(*args)
            memo[args] = res
            return res
    return wrap_func
