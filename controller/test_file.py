#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging

from tornado.gen import coroutine
from tornado.web import HTTPError
from tornado.options import options

from util.base_handler import BaseHandler, BaseDownloadHandler
from util import data_file, file_util
from bl import test_file as tf_bl


class TestFileHandler(BaseHandler):
    """
    上传插件fileinput
    """
    def get(self):
        self.render('test_fileinput.html')

    def post(self):
        action = self.get_argument('action')

        if action == "upload_file":
            files = self.request.files['input_file']
            _ = tf_bl.unzip_img_files(self, files[0]['body'])
            # unzip_img_files(self, files[0]['body'])
            # show_pretty_dict(res)
            """
            fio = StringIO.StringIO(files[0]['body'])
            zip_file = zipfile.ZipFile(file=fio)
            res = []
            for i in zip_file.namelist():
                res.append(save_oss(self.bucket, "img", zip_file.read(i), ".jpg"))
            show_pretty_dict(res)
            """
            self.write({})
        else:
            raise HTTPError(400)


class BaseSampleUpload(BaseHandler):
    show_title = ""

    def check_xsrf_cookie(self):
        pass

    def get(self):
        files = list(self.db.upload_history.find())
        tf_bl.set_file_path(self, files)
        self.render('test_sample_upload.html', files=files, title=self.show_title)

    def post(self):
        # TODO BLError
        data = self.request.files['txtStr'][0]['body']

        self.save_file(data, 'txt')
        self.write({'upload': "ok", 'status': 1})

    def save_file(self, content, ext):
        # need overwrite
        raise HTTPError(501, "need overwrite")


class OssUploadHandler(BaseSampleUpload):
    def initialize(self):
        self.show_title = 'oss'

    def save_file(self, content, ext):
        file_name = file_util.save_oss(self.oss_bucket, "doc", content, ".txt")
        self.db.upload_history.update({
            'file_name': file_name},
            {'$set':
                {'file_name': file_name,
                 'dest': 'oss'}
             }, upsert=True)


class LocalUploadHandler(BaseSampleUpload):
    def initialize(self):
        self.show_title = 'local'

    def save_file(self, content, ext):
        file_name = data_file.data_save(options.test_path, content, ".txt")
        self.db.upload_history.update({
            'file_name': file_name},
            {'$set':
                {'file_name': file_name,
                 'dest': 'local'}
             }, upsert=True)


class TestDownloadHandler(BaseDownloadHandler):

    def initialize(self):
        self.root = options.test_path

    def head(self, file_name):
        return self.get(file_name, include_body=False)

    @coroutine
    def get(self, file_name, include_body=True):
        file_name = "%s.txt" % file_name

        self.absolute_path = None
        logging.info('download file, file_name: {}, root: {}'.format(
            file_name, self.root
        ))
        fullpath = data_file.fullpath(self.root, file_name)
        self.path = self.request.path
        logging.info('fullpath: {}, self.path: {}, include_body: {}'.format(
            fullpath, self.path, include_body
        ))
        super(TestDownloadHandler, self).get(os.path.abspath(fullpath), include_body)
