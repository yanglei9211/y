#!/usr/bin/env python
# encoding=utf-8


import os
import datetime
import logging

from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line, parse_config_file
from jinja2 import ChoiceLoader, FileSystemLoader

import settings
from util.template import JinjaLoader
from util.common import install_tornado_shutdown_handler
from routes import get_routes


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

        loader = ChoiceLoader([
            FileSystemLoader(os.path.join(self_dir_path, 'templates')),
        ])
        the_settings = {
            'template_loader': JinjaLoader(loader=loader),
            'debug': options.debug,
            'cookie_secret': options.cookie_secret,
            'xsrf_cookies': True,
            'static_path': os.path.join(os.path.dirname(__file__), "static")
        }

        the_settings.update(more_settings)
        routes = get_routes()
        self.app = Application(routes, **the_settings)
        self.app.settings['template_loader'].env.globals.update({
            'options': options,
            'datetime': datetime.datetime,
        })

    def setup_db_client(self):
        pass

    def setup_user_db(self):
        pass

    def setup_oss_bucket(self):
        pass

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
