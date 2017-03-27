#!/usr/bin/env python
# encoding=utf-8

import sys
import os
import datetime
import logging

import oss2
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line, parse_config_file
from jinja2 import ChoiceLoader, FileSystemLoader
from pymongo import MongoClient
# from motor.motor_tornado import MotorClient

import settings
from util.template import JinjaLoader
from util.common import install_tornado_shutdown_handler
from util.request_handlers import SmartStaticFileHandler, MultiFileFindler
from routes import get_routes

reload(sys)
sys.setdefaultencoding('utf-8')
del sys.setdefaultencoding
del sys


class YWeb(object):
    def __init__(self, **more_settings):
        settings.define_app_options()
        parse_command_line(final=False)
        self_dir_path = os.path.abspath(os.path.dirname(__file__))
        if options.debug:
            conf_file_path = os.path.join(self_dir_path, 'server.conf')
        else:
            pass
        if os.path.exists(conf_file_path):
            parse_config_file(conf_file_path, final=False)
        parse_command_line(final=True)

        """
        loader = ChoiceLoader([
            FileSystemLoader(os.path.join(self_dir_path, 'templates')),
        ])
        """
        loader = JinjaLoader(loader=ChoiceLoader([
            FileSystemLoader(os.path.join(self_dir_path, 'templates')),
        ]), debug=options.debug)
        SmartStaticFileHandler.file_finder = MultiFileFindler(
            [],
            os.path.join(self_dir_path, 'static'))
        the_settings = {
            'template_loader': loader,
            'debug': options.debug,
            'cookie_secret': options.cookie_secret,
            'xsrf_cookies': True,
            'db': self.setup_db_client(),
            'asy_db': self.setup_asy_db_client(),
            'userdb': self.setup_user_db(),
            'oss_bucket': self.setup_oss_bucket(),
            'static_path': u'/static/',
            'static_handler_class': SmartStaticFileHandler,
        }

        the_settings.update(more_settings)
        routes = get_routes()
        self.app = Application(routes, **the_settings)
        self.app.settings['template_loader'].env.globals.update({
            'options': options,
            'datetime': datetime.datetime,
        })

    def setup_db_client(self):
        client = MongoClient(options.mongodb_host, options.mongodb_port)
        db = client[options.mongodb_name]
        logging.info('Connected to db: %s --- %s:%d' %
                     (options.mongodb_name, options.mongodb_host, options.mongodb_port))
        return db

    def setup_asy_db_client(self):
        """
        client = MotorClient(options.mongodb_host, options.mongodb_port)
        asy_db = client[options.mongodb_name]
        logging.info('Connected to asy_db: %s --- %s:%d' %
                     (options.mongodb_name, options.mongodb_host, options.mongodb_port))
        return asy_db
        """
        return None

    def setup_user_db(self):
        client = MongoClient(options.userdb_host, options.userdb_port)
        userdb = client[options.userdb_name]
        logging.info('Connected to userdb: %s --- %s: %d' %
                     (options.userdb_host, options.userdb_port, options.userdb_name))
        return userdb

    def setup_oss_bucket(self):
        auth = oss2.Auth(options.oss_access_id, options.oss_access_key)
        bucket = oss2.Bucket(auth, options.oss_endpoint, options.oss_name)
        return bucket

    def run(self):
        logging.info('Running at port %s in %s mode'
                     % (options.port, 'debug' if options.debug else 'production'))
        server = HTTPServer(self.app, xheaders=True)
        server.listen(options.port)
        install_tornado_shutdown_handler(IOLoop.instance(), server)
        logging.info('Good to go!')

        IOLoop.instance().start()
        logging.info('Exiting...waiting for backgroundparse_command_line(final=True) jobs done...')
        logging.info('Done. Bye.')


if __name__ == "__main__":
    y_server = YWeb()
    y_server.run()
