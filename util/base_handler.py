#!/usr/bin/env python
# encoding=utf-8
import logging

from tornado import httputil
from tornado.util import bytes_type
from tornado.web import RequestHandler
from tornado.web import StaticFileHandler
from tornado.options import options
from tornado.escape import json_decode

from bson.json_util import dumps, loads
from util.escape import json_encode, safe_typed_from_str
from util.common import force_browser_download_content
from errors import BLError

from app_define import USER_ROLE_MANAGER, USER_ROLE_FULL, USER_ROLE_PARTIAL


class BaseHandler(RequestHandler):
    allow_anony = False

    def prepare(self):
        uri = self.request.uri
        path = self.request.path
        user = self.current_user
        logging.info('user:%s is accessing %s' % (user, uri))

        if user is None and not self.allow_anony:
            self.redirect('/user/login')
            return

    def get_main_domain(self):
        host = self.request.host.split(':')[0]
        if ".com" not in self.request.host:
            return host
        else:
            return '.' + '.'.join(host.split('.')[-3:])

    def get_debug_user(self):
        user = dict(role=USER_ROLE_MANAGER, name=u'debug',
                    username="debug@local.host", email='debug@local.host')
        return user

    def get_current_user(self):
        if options.debug:
            return self.get_debug_user()

        user_json = self.get_secure_cookie('user')
        if user_json:
            user = json_decode(user_json)
            user_db = self.userdb.user.find_one({'username': user['username']})
            if user_db and user_db['valid'] and user['login_sn'] == self.get_cookie("login_sn"):
                user['name'] = user_db['name']
                user['role'] = user_db['role']
                return user
            else:
                self.clear_cookie('user', domain=self.get_main_domain())
                return None
        else:
            return None

    def get_logout_url(self):
        return "/user/logout"

    def get_login_url(self):
        return "/user/login"

    @property
    def m(self):
        return self.current_user['username'] if self.current_user else None

    @property
    def is_manager(self):
        return self.current_user and self.current_user['role'] == USER_ROLE_MANAGER

    @property
    def userdb(self):
        return self.application.settings.get('userdb')

    @property
    def db(self):
        return self.application.settings.get('db')

    @property
    def asy_db(self):
        return self.application.settings.get('asy_db')

    @property
    def oss_bucket(self):
        return self.application.settings.get('oss_bucket')

    # 权限管理
    @property
    def is_manager(self):
        return self.current_user['role'] == USER_ROLE_MANAGER if self.current_user else False

    @property
    def can_handler_user(self):
        return self.is_manager

    def get_argument(self, name, *args, **kwargs):
        type_ = kwargs.pop("type_" ,None)
        arg = super(BaseHandler, self).get_argument(name, *args, **kwargs)
        if type_ and isinstance(arg, basestring):
            return safe_typed_from_str(arg, type_)
        else:
            return arg

    def write(self, chunk):
        """
            override write to support our json_encode
        """
        if isinstance(chunk, dict):
            chunk = json_encode(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        super(BaseHandler, self).write(chunk)

    def write_error(self, status_code, **kwargs):
        if status_code == 403:
            self.write('no previlege')
            return
        else:
            return super(BaseHandler, self).write_error(status_code, **kwargs)

    def _handle_request_exception(self, e):
        # adapted from tornado
        # doubt whether this is a good idea
        if isinstance(e, BLError):
            if self.is_ajax_request():
                self.write({
                    'error_msg': e.message
                })
            else:
                self.write(e.message)
            if not self._finished:
                self.finish()
            return

        return super(BaseHandler, self)._handle_request_exception(e)

    def is_ajax_request(self):
        return self.request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def render(self, template, **kwargs):
        # TODO render common date
        # TODO top nav
        return super(BaseHandler, self).render(
            template, **kwargs)

    def dumps(self, obj):
        return dumps(obj, ensure_ascii=False, indent=4, sort_keys=True)

    @staticmethod
    def loads(s):
        return loads(s)


class BaseDownloadHandler(BaseHandler, StaticFileHandler):
    '''
    don't touch me unless you understand MRO !!

    override get, change any arguments into necessary absolute path
    '''
    def get(self, absolute_path, include_body=True):
        '''
        this is mostly copied from tornado
        '''
        # Set up our path instance variables.
        assert hasattr(self, 'path')
        assert hasattr(self, 'root')
        self.absolute_path = self.validate_absolute_path(self.root, absolute_path)
        if self.absolute_path is None:
            return

        self.modified = self.get_modified_time()
        self.set_headers()

        if self.should_return_304():
            self.set_status(304)
            return

        request_range = None
        range_header = self.request.headers.get("Range")
        if range_header:
            # As per RFC 2616 14.16, if an invalid Range header is specified,
            # the request will be treated as if the header didn't exist.
            request_range = httputil._parse_request_range(range_header)

        size = self.get_content_size()
        if request_range:
            start, end = request_range
            if (start is not None and start >= size) or end == 0:
                # As per RFC 2616 14.35.1, a range is not satisfiable only: if
                # the first requested byte is equal to or greater than the
                # content, or when a suffix with length 0 is specified
                self.set_status(416)  # Range Not Satisfiable
                self.set_header("Content-Type", "text/plain")
                self.set_header("Content-Range", "bytes */%s" % (size, ))
                return
            if start is not None and start < 0:
                start += size
            if end is not None and end > size:
                # Clients sometimes blindly use a large range to limit their
                # download size; cap the endpoint at the actual file size.
                end = size
            # Note: only return HTTP 206 if less than the entire range has been
            # requested. Not only is this semantically correct, but Chrome
            # refuses to play audio if it gets an HTTP 206 in response to
            # ``Range: bytes=0-``.
            if size != (end or size) - (start or 0):
                self.set_status(206)  # Partial Content
                self.set_header("Content-Range",
                                httputil._get_content_range(start, end, size))
        else:
            start = end = None

        if start is not None and end is not None:
            content_length = end - start
        elif end is not None:
            content_length = end
        elif start is not None:
            content_length = size - start
        else:
            content_length = size
        self.set_header("Content-Length", content_length)

        if include_body:
            content = self.get_content(self.absolute_path, start, end)
            if isinstance(content, bytes_type):
                content = [content]
            for chunk in content:
                self.write(chunk)
                self.flush()
        else:
            assert self.request.method == "HEAD"

    def set_extra_headers(self, path):
        '''
        @override
        '''
        fname = self.get_argument('fname', u'')
        # force browser to save file with name fname instead of opening it
        if fname:
            force_browser_download_content(self, fname)

        ua = self.request.headers.get("User-Agent")
        if ua and "MSIE 8." in ua:
            # 修复IE8下载https链接文档的bug
            # 见 https://support.microsoft.com/en-us/kb/323308
            self.set_header("Pragma", "private")
            self.clear_header("Cache-Control")
            self.clear_header("Expires")

    @classmethod
    def get_absolute_path(cls, root, path):
        raise NotImplementedError()

    @classmethod
    def make_static_url(cls, settings, path):
        raise NotImplementedError()

    @classmethod
    def get_version(cls, settings, path):
        raise NotImplementedError()