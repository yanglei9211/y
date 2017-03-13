#!/usr/bin/env python
# encoding: utf-8
import re
import time
import urllib
import zipfile
import StringIO
from time import sleep

import tornado
import requests
from tornado.gen import coroutine, Return, Task
from tornado.httpclient import AsyncHTTPClient
from util.file_util import save_oss


@coroutine
def asy_add(handler, a, b):
    yield Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time()+5)
    raise Return(a+b)


def add(a, b):
    sleep(5.0)
    return a + b


def im_add(a, b):
    return a + b


def unzip_img_files(handler, file_body):
    fio = StringIO.StringIO(file_body)
    zip_file = zipfile.ZipFile(file=fio)
    ques_nums = 0
    ques_imgs = []
    match_num = re.compile(ur"(\d+)-(\d+)")
    for img in zip_file.namelist():
        img_name = save_oss(handler.bucket, "img", zip_file.read(img), "png")
        res = match_num.search(img)

        if not res:
            raise Exception(u"图片文件名有误")
        v_num = int(res.group(2))
        if v_num == 1:
            ques_imgs.append([])
            ques_nums += 1
            ques_imgs[ques_nums-1].append(img_name)
        else:
            ques_imgs[ques_nums-1].append(img_name)
    return ques_imgs


@coroutine
def test_motor_find(handler):
    res = yield handler.asy_db.text_info.find().to_list(length=1000000)
    res = [t['t_id'] for t in res]
    raise Return(res)


def test_mongo_find(handler):
    res = handler.db.text_info.find()
    res = [t['t_id'] for t in res]
    return res


@coroutine
def asy_get_simhash(data):
    client = AsyncHTTPClient()
    data = {'action': 'calc_simhash', 'ques_data': data,
            'subject':'math', 'edu': 'junior'}
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
