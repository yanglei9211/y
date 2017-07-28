#!/usr/bin/env python
# encoding: utf-8
import re
import os
import StringIO
import zipfile

from tornado.options import options

from util import file_util
from util import data_file


def set_file_path(handler, files):

    def set_path(f):
        f['file_path'] = f['file_name'] if f['dest'] == 'local' else \
            file_util.fullpath(f['file_name'])

    map(set_path, files)


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


def fetch_file_list(handler):
    _data = list(handler.db.upload_history.find())
    return _data


def package_files(handler, files):
    z = zipfile.ZipFile('temp.zip', 'w')
    for f in files:
        content = data_file.data_open(options.test_path, f['file_name']).read() \
            if f['dest'] == 'local' \
            else file_util.open_oss(handler.oss_bucket, f['file_name']).read()
        z.writestr(f['file_name'], content)
    z.close()
    with open('temp.zip', 'r') as z_obj:
        zip_tmp = z_obj.read()
        zip_name = data_file.data_save(options.test_zip_path, zip_tmp, ".zip")
    os.remove('temp.zip')
    return zip_name
