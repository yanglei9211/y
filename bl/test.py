#!/usr/bin/env python
# encoding: utf-8

from tornado.gen import coroutine, Return
from time import sleep


@coroutine
def asy_add(handler, a, b):
    sleep(2.0)
    raise Return(a+b)


def add(a, b):
    sleep(2.0)
    return a + b
