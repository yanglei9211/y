#!/usr/bin/env python
# encoding: utf-8

import re
import time
import signal
import httpagentparser

from tornado.escape import url_escape


MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 1


def install_tornado_shutdown_handler(ioloop, server, logger=None):
    # see https://gist.github.com/mywaiting/4643396 for more detail
    if logger is None:
        import logging
        logger = logging

    def _sig_handler(sig, frame):
        logger.info("Signal %s received. Preparing to stop server.", sig)
        ioloop.add_callback(shutdown)

    def shutdown():
        logger.info("Stopping http server...")
        server.stop()
        logger.info("will shutdown in %s seconds", MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

        def stop_loop():
            now = time.time()
            if now < deadline and (ioloop._callbacks or ioloop._timeouts):
                ioloop.add_timeout(now + 1, stop_loop)
                logger.debug("Waiting for callbacks and timesouts in IOLoop...")
            else:
                ioloop.stop()
                logger.info("Server is shutdown")
        stop_loop()

    signal.signal(signal.SIGTERM, _sig_handler)
    signal.signal(signal.SIGINT, _sig_handler)
