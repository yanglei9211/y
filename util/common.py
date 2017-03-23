#!/usr/bin/env python
# encoding: utf-8

import re
import time
import signal

import httpagentparser
from tornado.escape import url_escape


MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 1
PAGE_SIZE_DEFAULT = 20


def install_tornado_shutdown_handler(ioloop, server, logger=None):
    # see https://gist.github.com/mywaiting/4643396 for more detail
    if logger is None:
        import logging
        logger = logging

    def _sig_handler(sig, frame):
        logger.info("Signal %s received. Preparing to stop server.", sig)
        ioloop.add_callback(shutdown)

    def shutdown():
        logger.info("Stopping http server...")
        server.stop()
        logger.info("will shutdown in %s seconds", MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

        def stop_loop():
            now = time.time()
            if now < deadline and (ioloop._callbacks or ioloop._timeouts):
                ioloop.add_timeout(now + 1, stop_loop)
                logger.debug("Waiting for callbacks and timesouts in IOLoop...")
            else:
                ioloop.stop()
                logger.info("Server is shutdown")
        stop_loop()

    signal.signal(signal.SIGTERM, _sig_handler)
    signal.signal(signal.SIGINT, _sig_handler)


class Pager:
    def __init__(self, handler):
        self.page_count = 0
        self.page = handler.get_argument('page_idx', 0, type_=int)
        self.page_size = handler.get_argument('page_size', PAGE_SIZE_DEFAULT, type_=int)
        self.page_size = min(100, max(1, self.page_size))

    def paginate(self, cursor):
        cursor.limit(self.page_size)
        if self.page > 0:
            cursor.skip(self.page_size * self.page)
        self.page_count = self.count_page_num(cursor.count())
        return cursor

    def paged_response(self):
        return {
            'page': self.page,
            'pagecount': self.page_count,
            'pagesize': self.page_size
        }

    def count_page_num(self, total_count):
        res = total_count / self.page_size
        if total_count % self.page_size:
            res += 1
        return res


_INVALID_HTTP_HEADER_CHAR_RE = re.compile(br"[\x00-\x1f]")


def filter_unsafe_http_header_value(value):
    return _INVALID_HTTP_HEADER_CHAR_RE.sub(' ', value)


def force_browser_download_content(handler, fname):
    fname = filter_unsafe_http_header_value(fname)
    if not fname:
        fname = u'未命名'
    agent = httpagentparser.detect(handler.request.headers.get('User-Agent', u''))
    browser = agent.get('browser', None) if agent else None
    header_set = False
    escaped_fname = url_escape(fname, False)
    if browser:
        if browser.get('name', u'') == 'Microsoft Internet Explorer' and\
                browser.get('version', u'') in ('7.0', '8.0'):
            handler.set_header('Content-Disposition',
                               'attachment;filename={}'.format(escaped_fname))
            header_set = True
    if not header_set:
        handler.set_header('Content-Disposition',
                           'attachment;filename="{}";filename*=UTF-8\'\'{}'.format(
                               fname.encode('utf-8'), escaped_fname))
