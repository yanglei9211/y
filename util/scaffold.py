#!/usr/bin/env python
# encoding: utf-8

import time
import logging
import os

from tornado.options import options, parse_command_line, parse_config_file
from pymongo import MongoClient

import settings


class Scaffold(object):

    def __init__(self):
        self.setup()

    def setup(self):
        settings.define_app_options()
        parse_command_line(final=False)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logging.info('Running in %s mode' % ('debug' if options.debug else 'production'))
        print '#' * 23
        print options.debug

        if options.debug:
            conf_file_path = os.path.join(current_dir, 'server.conf')
        else:
            conf_file_path = os.path.join(current_dir, 'prod.conf')

        if os.path.exists(conf_file_path):
            parse_config_file(conf_file_path, final=False)

        parse_command_line(final=True)
        self.db = self.setup_db()
        self.userdb = self.setup_userdb()

    def setup_db(self):
        db_name = options.mongodb_name
        db = MongoClient(options.mongodb_host, options.mongodb_port)[db_name]
        logging.info('Connexted to db %s:%d ' % (options.mongodb_host, options.mongodb_port))
        return db

    def setup_userdb(self):
        db_name = options.userdb_name
        userdb = MongoClient(options.userdb_host, options.userdb_port)[db_name]
        logging.info('Connexted to db %s:%d ' % (options.userdb_host, options.userdb_port))
        return userdb

    def timeit(self, fn, *args, **kwargs):
        t1 = time.clock()
        ret = fn(*args, **kwargs)
        t2 = time.clock()
        return t2 - t1, ret

    def run(self, *args, **kwargs):
        return self.main(*args, **kwargs)

    def main(self, *args, **kwargs):
        # overwrite
        assert False
