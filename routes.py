#!/usr/bin/env python
# encoding: utf-8


def get_routes():
    routes = [

        (r'/user/login', 'controller.user.LoginHandler'),
        (r'/user/logout', 'controller.user.LogoutHandler'),

        (r'/test/sync', 'controller.test.TestNormalHandler'),
        (r'/test/async', 'controller.test.TestHandler'),

        (r'/weibo', 'controller.weibo.WeiboHandler'),
        (r'/', 'controller.weibo.WeiboHandler')
    ]
    return routes
