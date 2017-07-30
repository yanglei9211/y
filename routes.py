#!/usr/bin/env python
# encoding: utf-8


def get_routes():
    routes = [

        (r'/user/login', 'controller.user.LoginHandler'),
        (r'/user/logout', 'controller.user.LogoutHandler'),

        (r'/weibo', 'controller.weibo.WeiboHandler'),
        (r'/', 'controller.weibo.WeiboHandler')
    ]
    return routes
