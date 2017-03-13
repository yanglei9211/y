#!/usr/bin/env python
# encoding: utf-8
import sys
import zipfile
import StringIO

from util.base_handler import BaseHandler
from tornado.gen import coroutine
from tornado.web import HTTPError

from bl.test import asy_add, add
from util.escape import safe_typed_from_str
from util.file_util import save_oss

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
        self.finish()


class TestNormalHandler(BaseHandler):

    def get(self):
        a = safe_typed_from_str(self.get_argument('a'), int)
        b = safe_typed_from_str(self.get_argument('b'), int)
        res = add(a, b)
        self.write({'ans': res})


class TestFileHandler(BaseHandler):

    def get(self):
        db = self.db
        self.render('test_fileinput.html')

    def post(self):
        action = self.get_argument('action')

        if action == "upload_file":
            files = self.request.files['input_file']
            print files[0]['filename']
            # print files[0]['body']
            # fd = open(files[0]['body'])
            fio = StringIO.StringIO(files[0]['body'])
            zip_file = zipfile.ZipFile(file=fio)
            res = []
            for i in zip_file.namelist():
                res.append(save_oss(self.bucket, "img", zip_file.read(i), ".jpg"))
            show_pretty_dict(res)
        else:
            raise HTTPError(400)
