#!/usr/bin/env python
# encoding: utf-8
import re
import sys
import zipfile
import StringIO

from util.base_handler import BaseHandler
from tornado.gen import coroutine
from tornado.web import HTTPError

from bl.test import asy_add, add, im_add
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


class TestImHandler(BaseHandler):
    def get(self):
        a = safe_typed_from_str(self.get_argument('a'), int)
        b = safe_typed_from_str(self.get_argument('b'), int)
        res = im_add(a, b)
        self.write({'ans': res})


class TestFileHandler(BaseHandler):

    def get(self):
        db = self.db
        self.render('test_fileinput.html')

    def post(self):
        action = self.get_argument('action')

        if action == "upload_file":
            files = self.request.files['input_file']
            res = self.unzip_img_files(files[0]['body'])
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

    def unzip_img_files(self, file_body):
        fio = StringIO.StringIO(file_body)
        zip_file = zipfile.ZipFile(file=fio)
        ques_nums = 0
        ques_imgs = []
        match_num = re.compile(ur"(\d+)-(\d+)")
        for img in zip_file.namelist():
            img_name = save_oss(self.bucket, "img", zip_file.read(img), "png")
            res = match_num.search(img)
            print res.group()
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
