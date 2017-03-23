#!/usr/bin/env python
# encoding=utf-8

import logging
import hashlib

from oss2.exceptions import OssError


def save_oss(bucket, prefix, content, ext=""):
    digest = hashlib.md5(content).hexdigest()
    filename = prefix + "-" + digest
    if ext:
        if ext.startswith('.'):
            filename += ext
        else:
            filename += '.' + ext
    try:
        filename = filename.lower()
        bucket.put_object(filename, content)
        print "ok"
    except OssError as e:
        print "fail"
        logging.error("save_oss put_object except with: %s" % str(e))
        return ""
    return filename


def open_oss(bucket, filename):
    pass


def full_path(file_name):
    return "http://erich.oss-cn-beijing.aliyuncs.com/" + file_name
