#!/usr/bin/env python
# encoding: utf-8

import re
import logging
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


class TextWriter(object):
    def __init__(self, **kwargs):
        self.method = kwargs.get("method", "cmd")       # cmd, file, logging
        self.with_linenum = kwargs.get("with_linenum", False)
        self.file_name = kwargs.get("file_name", "new_file.txt")
        self.caches = []

    def set_method(self, s):
        self.method = s

    def set_linenum(self, f):
        self.with_linenum = f

    def set_file_name(self, f):
        self.file_name = f

    def write(self, s):
        idx = len(self.caches) - 1
        if idx < 0:
            idx += 1
            self.caches.append("")
        self.caches[idx] += s

    def writeln(self, s):
        self.caches.append(s)

    def write_pretty(self, s):
        def _combined(val):
            """
            判断val是不是dict或者list
            :param val:
            :return: none
            """
            if isinstance(val, list) or isinstance(val, dict) or isinstance(val, tuple):
                return True
            return False

        def _write_pretty(val, write_caches, deep=0):
            """
            格式化输出，用来调试
            :param show_mode:
            :param val:
            :param deep:
            :return: None
            """
            if isinstance(val, dict):
                for r in val:
                    if _combined(val[r]):
                        write_caches.append(u"%s%s:" % ('\t' * deep, r))
                        _write_pretty(val[r], write_caches, deep + 1)
                    else:
                        write_caches.append(u"%s%s:%s" % ("\t" * deep, r, val[r]))

            elif isinstance(val, list) or isinstance(val, tuple):
                for i, r in enumerate(val):
                    if _combined(val[i]):
                        write_caches.append(u"%s%d:" % ("\t" * deep, i))
                        _write_pretty(val[i], write_caches, deep + 1)
                    else:
                        write_caches.append(u"%s%d:%s" % ("\t" * deep, i, val[i]))
            else:
                write_caches.append(u"%s:%s" % ("\t" * deep, val))

        _caches = []
        _write_pretty(s, _caches)
        self.caches.extend(_caches)

    def clear(self):
        self.caches = []

    def commit(self):
        if self.method == "file":
            with open(self.file_name, "w") as f:
                for out_str in self._datas():
                    f.write("%s\n" % out_str)
        else:
            for out_str in self._datas():
                if self.method == "cmd":
                    print out_str
                elif self.method == "logging":
                    logging.info(out_str)

    def _datas(self):
        for i, s in enumerate(self.caches):
            if self.with_linenum:
                yield u"%d\t|\t%s" % (i+1, s)
            else:
                yield u"%s" % s
