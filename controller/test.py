#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging

from util.base_handler import BaseHandler, BaseDownloadHandler
from tornado.options import options
from tornado.gen import coroutine
from tornado.web import HTTPError

from bl.test import asy_add, add, im_add
from bl.test import test_motor_find, test_mongo_find
from bl.test import get_simhash, asy_get_simhash
from util.escape import safe_typed_from_str
from util import file_util, data_file

from debug_func import show_pretty_dict

reload(sys)
sys.setdefaultencoding('utf-8')


class TestHandler(BaseHandler):
    @coroutine
    def get(self):
        a = safe_typed_from_str(self.get_argument('a'), int)
        b = safe_typed_from_str(self.get_argument('b'), int)
        res = yield asy_add(self, a, b)
        self.write({'ans': res})


class TestNormalHandler(BaseHandler):

    def get(self):
        a = safe_typed_from_str(self.get_argument('a'), int)
        b = safe_typed_from_str(self.get_argument('b'), int)
        res = add(a, b)
        self.write({'ans': res})


class TestImHandler(BaseHandler):
    def get(self):
        a = safe_typed_from_str(self.get_argument('a'), int)
        b = safe_typed_from_str(self.get_argument('b'), int)
        res = im_add(a, b)
        self.write({'ans': res})


class TestMotorHandler(BaseHandler):
    @coroutine
    def get(self):
        res = yield test_motor_find(self)
        self.write({'data': res})


class TestMongoHandler(BaseHandler):
    def get(self):
        res = test_mongo_find(self)
        self.write({'data': res})


class TestAsyHttpClient(BaseHandler):
    @coroutine
    def get(self, t_id):
        ques_data = self.db.text_info.find_one({'t_id': str(t_id)})['data']
        ques_data = "aksjhdfjkladshfkjladshfkjladshfkadjlshdfkladshfkladjeiojkrf"
        res = yield asy_get_simhash(ques_data)
        self.write({'s': res.body})


class TestHttpClient(BaseHandler):
    def get(self, t_id):
        ques_data = self.db.text_info.find_one({'t_id': t_id})['data']
        ques_data = "aksjhdfjkladshfkjladshfkjladshfkadjlshdfkladshfkladjeiojkrf"
        res = get_simhash(ques_data)
        self.write({'s': res.text})


class TestGenList(BaseHandler):
    def get(self):
        teacher_name = self.get_argument('teacher_username')
        print teacher_name
        res = [
            {'student_username': "a", 'student_display_name': "aaa", 'class_name': "111"},
            {'student_username': "b", 'student_display_name': "bbb", 'class_name': "222"},
            {'student_username': "c", 'student_display_name': "ccc", 'class_name': "333"},
            {'student_username': "d", 'student_display_name': "ddd", 'class_name': "444"},
            {'student_username': "e", 'student_display_name': "eee", 'class_name': "555"},
            {'student_username': "f", 'student_display_name': "fff", 'class_name': "666"},
            {'student_username': "g", 'student_display_name': "ggg", 'class_name': "777"},
            {'student_username': "h", 'student_display_name': "hhh", 'class_name': "888"},
            {'student_username': "i", 'student_display_name': "iii", 'class_name': "999"},
            {'student_username': "j", 'student_display_name': "jjj", 'class_name': "121"},
            {'student_username': "k", 'student_display_name': "kkk", 'class_name': "122"},

        ]
        self.write({'body': res})


