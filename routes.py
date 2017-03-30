#!/usr/bin/env python
# encoding: utf-8


def get_routes():
    routes = [
        (r'/first', 'controller.first.FirstHandler'),
        (r'/tree', 'controller.ztree.TreeHandler'),
        (r'/test', 'controller.test.TestHandler'),
        (r'/test2', 'controller.test.TestNormalHandler'),
        (r'/test3', 'controller.test.TestImHandler'),
        (r'/test/motor/find', 'controller.test.TestMotorHandler'),
        (r'/test/mongo/find', 'controller.test.TestMongoHandler'),
        (r'/test/getsim/(\w+)', 'controller.test.TestHttpClient'),
        (r'/test/asygetsim/(\w+)', 'controller.test.TestAsyHttpClient'),

        (r'/test/fileinput', 'controller.test_file.TestFileHandler'),
        (r'/test/oss/file', 'controller.test_file.OssUploadHandler'),
        (r'/test/local/file', 'controller.test_file.LocalUploadHandler'),
        (r'/test/download/(.*).txt', 'controller.test_file.TextDownloadHandler'),
        (r'/test/download/(.*).zip', 'controller.test_file.ZipDownloadHandler'),
        (r'/test/zip', 'controller.test_file.ZipPackageHandler'),

        (r'/api/students', 'controller.test.TestGenList'),

        (r'/user/login', 'controller.user.LoginHandler'),
        (r'/user/logout', 'controller.user.LogoutHandler'),

        (r'/manager/user', 'controller.user.UserHandler'),
        (r'/manager/user/(\w+)', 'controller.user.UserHandler'),
        (r'/manager/users', 'controller.user.ListHandler'),


        (r'/main', 'controller.first.WelcomeHandler'),

    ]
    return routes
