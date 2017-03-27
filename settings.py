#!/usr/bin/env python
# encoding: utf-8

import logging
from tornado.options import define


def define_app_options():
    define('debug', default=True)
    define('log_level', default=logging.INFO)
    define('cookie_secret', default='dzwOrPqGdgOwBqyVdzwOrPqGdgOwBqyVdzwOrPqGdgOwBqyV')
    define('port', default=8080)

    define('mongodb_host', default='127.0.0.1')
    define('mongodb_port', default=27017)
    define('mongodb_name', default="test")

    define('userdb_host', default='127.0.0.1')
    define('userdb_port', default=27017)
    define('userdb_name', default='user')

    """
    define('mongodb_host', default='10.200.2.232')
    define('mongodb_port', default=23333)
    define('mongodb_name', default='cluster')
    """

    define('oss_access_id', default='LTAIVDL7MzrhpspZ'),
    define('oss_access_key', default='dLkT1LRxmASCVt2IJ6DmaFVkePdhPl'),
    define('oss_endpoint', 'http://oss-cn-beijing.aliyuncs.com')
    define('oss_name', 'erich')

    define('test_path', default='data/test/')
    define('test_zip_path', default='data/test/zip/')
