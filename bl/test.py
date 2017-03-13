#!/usr/bin/env python
# encoding: utf-8

import tornado
from tornado.gen import coroutine, Return, Task
import time
from time import sleep


@coroutine
def asy_add(handler, a, b):
    yield Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time()+5)
    raise Return(a+b)


def add(a, b):
    sleep(5.0)
    return a + b


def im_add(a, b):
    return a + b
