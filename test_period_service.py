#!/usr/bin/env python
# encoding: utf-8
import logging
import random

from pymongo import UpdateOne

from util.decorator import show_time_cost
from util.service import Service


class PeriodService(Service):
    def main(self):
        logging.info('Start to work')
        flag = self.db.test.find_one()
        if not flag:
            self.data_init()
        else:
            tests = self.db.test.find()
            ids = [t['_id'] for t in tests]
            self.test_mul_update(ids)
            self.test_update(ids)

    @show_time_cost
    def data_init(self):
        for i in range(10000):
            self.db.test.insert(
                {'a': 1, 'b': 2, 'c': 3}
            )

    @show_time_cost
    def test_update(self, ids):
        for _id in ids:
            self.db.test.update({'_id': _id},
                                {'$set': {
                                    'a': random.randint(1, 100),
                                    'b': random.randint(1, 100),
                                    'c': random.randint(1, 100),
                                }})

    @show_time_cost
    def test_mul_update(self, ids):
        requests = []
        for _id in ids:
            requests.append(
                UpdateOne({'_id': _id},
                          {'$set': {
                              'a': random.randint(1, 100),
                              'b': random.randint(1, 100),
                              'c': random.randint(1, 100),
                          }})
            )


if __name__ == "__main__":
    PeriodService(20).run()
