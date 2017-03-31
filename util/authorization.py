#!/usr/bin/env python
# encoding: utf-8

from tornado.web import HTTPError

from util.base_handler import BaseHandler


class ManagerHandler(BaseHandler):
    def prepare(self):
        super(ManagerHandler, self).prepare()
        if not self.can_handler_user:
            raise HTTPError(403)
