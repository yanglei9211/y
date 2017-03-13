#!/usr/bin/env python
# encoding: utf-8


def get_routes():
    routes = [
        (r'/first', 'controller.first.FirstHandler'),
        (r'/tree', 'controller.ztree.TreeHandler'),
        (r'/test', 'controller.test.TestHandler'),
        (r'/test2', 'controller.test.TestNormalHandler'),
        (r'/test3', 'controller.test.TestImHandler'),
        (r'/test/fileinput', 'controller.test.TestFileHandler'),
    ]
    return routes
