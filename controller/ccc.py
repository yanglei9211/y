#!/usr/bin/env python
# encoding: utf-8

from simhash import Simhash

from util.base_handler import BaseHandler
from bl import ccc as cbl

from debug_func import show_time_cost


class CHandler(BaseHandler):
    @show_time_cost
    def post(self):
        action = self.get_argument("action")
        if action == "ques":
            tid = self.get_argument('text_id', type_=int)
            text = self.get_argument('text')
            sim = Simhash(text)
            res = cbl.ques(self, tid, sim)
            self.write({'data': res})
        elif action == "auto_cluster":
            tid = self.get_argument('text_id', type_=int)
            text = self.get_argument('text')
            sim = Simhash(text)
            rep = cbl.auto_clus(self, tid, text, sim)
            self.write({'data': rep})


