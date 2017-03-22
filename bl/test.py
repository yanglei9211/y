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

from debug_func import show_pretty_dict


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
    match_num = re.compile(ur"(\d+)-(\d+)")
    match_type = re.compile(ur"(?<=_)(\S+题)")
    img_list = []
    for _name in zip_file.namelist():
        img_name = _name.decode("gbk")
        res_num = match_num.search(img_name)
        res_type = match_type.search(img_name)
        assert res_num
        assert res_type
        # 保证文件名格式正确
        d = {'q_num': int(res_num.group(1)),
             'img_num': int(res_num.group(2)),
             "type": res_type.group(),
             # 'img_name': save_oss(handler.oss_bucket, "img", zip_file.read(_name), "png")
             'img_name': "temp",
             }
        img_list.append(d)

    img_list.sort(key=lambda x: (x['q_num'], x['img_num']))
    show_pretty_dict(img_list)
    print "#" * 23
    questions = []
    block = []
    for idx in range(len(img_list)):
        if idx == 0 or img_list[idx]['type'] == img_list[idx - 1]['type']:
            block.append(img_list[idx])
        else:
            questions.append(block)
            block = [img_list[idx]]
    if block:
        questions.append(block)

    show_pretty_dict(questions)
    return questions


def scan_files(file_body):
    fio = StringIO.StringIO(file_body)
    zip_file = zipfile.ZipFile(file=fio)
    mt_num = re.compile(ur"(\d+)-(\d+)")
    mt_type = re.compile(ur"(?<=_)(\S+题)")
    for img_name in zip_file.namelist():
        s = img_name.decode("gbk")
        r_num = mt_num.search(s)
        r_tp = mt_type.search(s)
        print r_num.group(1), r_num.group(2)
        print r_tp.group()
        # s = img_name
        # print s


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
