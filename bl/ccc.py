#!/usr/bin/env python
# encoding: utf-8

import time


def ques(handler, text_id, sim):
    res = handler.index.get_near_dups(text_id, sim)
    return res


def auto_clus(handler, text_id, text, sim):
    res = handler.index.get_near_dups(text_id, sim)
    cur = time.time()
    rep = res[0] if res else text_id
    is_rep = not res
    doc = {
        'text': text,
        'ctime': cur,
        'mtime': cur,
        'rep': is_rep,
        'rep_text_id': rep,
        'deleted': False,
        'simhash': format_hex(sim.value)
    }
    handler.db.data5.update({'text_id': text_id}, {'$set': doc}, upsert=True)
    handler.index.add(text_id, sim)
    return rep


def format_hex(x):
    x = int(x)
    s = hex(x)[2:18]
    if s[-1] == 'L':
        s = s[:-1]
    return s
