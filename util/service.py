#!/usr/bin/env python
# encoding: utf-8
import time
import logging
from functools import partial

from tornado.ioloop import IOLoop
from tornado.ioloop import PeriodicCallback

from scaffold import Scaffold


class Service(Scaffold):
    def __init__(self, interval=1):
        """
        interval is in sectionds
        """
        super(Service, self).__init__()
        self.interval = interval * 1000
        self.periodcalCb = None

    def stop(self):
        if self.periodcalCb:
            self.periodcalCb.stop()

    def pre(self):
        pass

    def run(self, *args, **kwargs):
        self.pre()
        super(Service, self).run(*args, **kwargs)
        self.periodcalCb = PeriodicCallback(
            partial(super(Service, self).run, *args, **kwargs),
            self.interval, IOLoop.instance()
        )
        self.periodcalCb.start()
        IOLoop.instance().start()

    def main(self):
        """
        overwrite
        """
        logging.error('Subclass main method... %s' % time.clock())
