#!/usr/bin/env python
# encoding: utf-8


def get_routes():
    routes = [
        (r'/first', 'controller.first.FirstHandler'),
        (r'/tree', 'controller.ztree.TreeHandler')
    ]
    return routes
