#!/usr/bin/env python
# encoding: utf-8

from tornado.options import options, define

from scrrun import Scaffold
from app_define import USER_ROLE_MANAGER
from bl.user import hash_pwd, create


class Env(object):
    def __init__(self):
        self.m = 'system'


class Runner(Scaffold):
    def main(self):
        env = Env()
        userdb = self.userdb
        username = options.username
        password = options.password
        name = options.name
        role = USER_ROLE_MANAGER
        password = hash_pwd(password, username)
        user = create(env, username, name, password, role)
        try:
            userdb.user.insert(user)
        except:
            print u"用户名已存在"
        else:
            print u"创建成功"


if __name__ == "__main__":
    define('username', default='root')
    define('password', default='123456')
    define('name', default='管理员')
    Runner().run()
