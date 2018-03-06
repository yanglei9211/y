#!/usr/bin/env python
# encoding: utf-8

from pymongo import MongoClient
from tornado.options import options
from simhash import SimhashIndex
from simhash import Simhash

from debug_func import show_time_cost


class SimIndex(object):
    @show_time_cost
    def __init__(self):
        self.db = MongoClient(options.mongodb_host, options.mongodb_port)[options.mongodb_name]
        res = list(self.db.data5.find({'deleted': False, 'rep': True}, fields=['text_id', 'simhash']
                                      ))
        nodes = []
        for doc in res:
            sim = Simhash(long(doc['simhash'], 16))
            nodes.append((doc['text_id'], sim))
        print "total docs: %d" % len(nodes)
        self.index = SimhashIndex(nodes)

    def get_near_dups(self, text_id, sim):
        res = self.index.get_near_dups(sim)
        res = filter(lambda x: x != text_id, res)
        return res

    def add(self, text_id, sim):
        self.index.add(text_id, sim)
