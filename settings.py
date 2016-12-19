#!/usr/bin/env python
# fileencoding=utf-8

import logging
from tornado.options import define


def define_app_options():
    define('debug', default=True)
    define('log_level', default=logging.INFO)
    define('cookie_secret', default='dzwOrPqGdgOwBqyVdzwOrPqGdgOwBqyVdzwOrPqGdgOwBqyV')
    define('port', default=8080)
    define('mongodb_host', default='127.0.0.1')
    define('mongodb_port', default=27017)
    define('mongodb_name', default='name')
