#!/usr/bin/env python
# encoding: utf-8
from util.base_handler import BaseHandler


class TreeHandler(BaseHandler):
    def get(self):
        self.render('ztree.html')
