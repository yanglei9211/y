#!/usr/bin/env python
# encoding: utf-8

from util.base_handler import BaseHandler


class FirstHandler(BaseHandler):
    def get(self):
        self.render(
            'first.html',
            name="123"
        )

    def post(self):
        a = self.get_argument('a')
        b = self.get_argument('b')
        self.write({'sum': a+b})
