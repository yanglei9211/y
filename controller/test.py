#!/usr/bin/env python
# encoding: utf-8

from util.base_handler import BaseHandler
from tornado.gen import coroutine
from tornado.web import HTTPError

from bl.test import asy_add, add, im_add
from bl.test import unzip_img_files
from bl.test import test_motor_find, test_mongo_find
from bl.test import get_simhash, asy_get_simhash
from util.escape import safe_typed_from_str

from debug_func import show_pretty_dict


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


class TestFileHandler(BaseHandler):

    def get(self):
        self.render('test_fileinput.html')

    def post(self):
        action = self.get_argument('action')

        if action == "upload_file":
            files = self.request.files['input_file']
            res = unzip_img_files(self, files[0]['body'])
            show_pretty_dict(res)
            """
            fio = StringIO.StringIO(files[0]['body'])
            zip_file = zipfile.ZipFile(file=fio)
            res = []
            for i in zip_file.namelist():
                res.append(save_oss(self.bucket, "img", zip_file.read(i), ".jpg"))
            show_pretty_dict(res)
            """
        else:
            raise HTTPError(400)


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
