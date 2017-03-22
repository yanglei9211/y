#!/usr/bin/env python
# encoding=utf-8
import logging

from tornado.web import RequestHandler
from tornado.options import options
from tornado.escape import json_decode

from bson.json_util import dumps, loads
from util.escape import json_encode, safe_typed_from_str
from errors import BLError

from app_define import USER_ROLE_MANAGER


class BaseHandler(RequestHandler):
    allow_anony = False

    def prepare(self):
        uri = self.request.uri
        path = self.request.path
        user = self.current_user
        logging.info('user:%s is accessing %s' % (user, uri))

        if user is None and not self.allow_anony:
            self.redirect('/auth/login')
            return

    def get_main_domain(self):
        host = self.request.host.split(':')[0]
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

    @property
    def m(self):
        return self.current_user['username'] if self.current_user else None

    @property
    def is_manager(self):
        return self.current_user and self.current_user['role'] == USER_ROLE_MANAGER

    @property
    def db(self):
        return self.application.settings.get('db')

    @property
    def asy_db(self):
        return self.application.settings.get('asy_db')

    @property
    def oss_bucket(self):
        return self.application.settings.get('oss_bucket')

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
        # todo render common date
        return super(BaseHandler, self).render(
            template, **kwargs)

    def dumps(self, obj):
        obj = self.sorted(obj)
        return dumps(obj, ensure_ascii=False, indent=4, sort_keys=True)

    @staticmethod
    def loads(s):
        return loads(s)
