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
        (r'/test/motor/find', 'controller.test.TestMotorHandler'),
        (r'/test/mongo/find', 'controller.test.TestMongoHandler'),
        (r'/test/getsim/(\w+)', 'controller.test.TestHttpClient'),
        (r'/test/asygetsim/(\w+)', 'controller.test.TestAsyHttpClient'),
        (r'/test/sample_upload', 'controller.test.TestSampleUpload'),

        (r'/api/students', 'controller.test.TestGenList'),
    ]
    return routes
