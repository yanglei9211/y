#!/usr/bin/env python
# encoding: utf-8


from util.base_handler import BaseHandler
from tornado.gen import coroutine

from bl.test import asy_add, add
from util.escape import safe_typed_from_str


class TestHandler(BaseHandler):
    @coroutine
    def get(self):
        a = safe_typed_from_str(self.get_argument('a'), int)
        b = safe_typed_from_str(self.get_argument('b'), int)
        res = yield asy_add(self, a, b)
        self.write({'ans': res})
        self.finish()


class TestNormalHandler(BaseHandler):

    def get(self):
        a = safe_typed_from_str(self.get_argument('a'), int)
        b = safe_typed_from_str(self.get_argument('b'), int)
        res = add(a, b)
        self.write({'ans': res})
