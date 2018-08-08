#!/usr/bin/env python
# encoding: utf-8
import time
import urllib
from time import sleep

import tornado
import requests
from tornado.gen import coroutine, Return, Task
from tornado.httpclient import AsyncHTTPClient


@coroutine
def asy_add(handler, a, b):
    yield Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time()+5)
    raise Return(a+b)


def add(a, b):
    sleep(5.0)
    return a + b


def im_add(a, b):
    return a + b


@coroutine
def test_motor_find(handler):
    res = yield handler.asy_db.raws2.find({'text_id': {'$gt': 1235152}}).to_list(100)
    # res = list(res)
    raise Return(res)


def test_mongo_find(handler):
    res = handler.db.raws2.find({'text_id': {'$gt': 12358585}}).limit(100)
    res = list(res)
    return res


@coroutine
def asy_get_simhash(data):
    client = AsyncHTTPClient()
    data = {'action': 'calc_simhash', 'ques_data': data,
            'subject': 'math', 'edu': 'junior'}
    url = 'http://10.200.2.232:8000/cluster/cluster_text'
    response = yield client.fetch(
        url,
        body=urllib.urlencode(data),
        method='POST'
    )
    raise Return(response)


def get_simhash(data):
    data = {'action': 'calc_simhash', 'ques_data': data,
            'subject': 'math', 'edu': 'junior'}
    url = 'http://10.200.2.232:8000/cluster/cluster_text'
    res = requests.post(url, data)
    return res
