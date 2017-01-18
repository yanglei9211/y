#!/usr/bin/env python
# encoding: utf-8
import time
import random
import logging

from tornado.web import HTTPError
from tornado.options import options

from util.base_handler import BaseHandler
from util.escape import safe_objectid_from_str
from bl.user import fetch_user
from bl.user import create as create_user
from bl.user import gen_salt, hash_pwd
from bl.user import assert_name_legal, assert_username_legal
from errors import BLError


class UserHandler(BaseHandler):

    def get(self, uid=None):
        if uid:
            uid = safe_objectid_from_str(uid)
            user = fetch_user(self, uid)
        else:
            user = None

        self.render('user/form.html', user=user)

    def post(self, uid=None):
        action = self.get_argument('action')
        if uid:
            uid = safe_objectid_from_str(uid)
        if action == 'create':
            self.create()
        elif action == 'save':
            self.save(uid)
        elif action == 'delete':
            self.delete(uid)
        else:
            raise HTTPError(400)
        self.write({})

    def delete(self, uid):
        user = fetch_user(self, uid)
        user['valid'] = not user['valid']
        self.userdb.user.update()

    def create(self):
        username = self.get_argument('username')
        assert_username_legal(username)
        name = self.get_argument('name')
        assert_name_legal(name)
        password = self.get_argument('password')
        user = create_user(self, 'username', name, password)
        try:
            self.userdb.user.insert(user)
        except:
            raise BLError(u'用户名已存在')

    def save(self, uid):
        name = self.get_argument('name')
        assert_name_legal(name)
        password = self.get_argument('password', '')
        up_set = {
            'name': name,
        }
        if password:
            salt = gen_salt()
            password = hash_pwd(password, salt)
            up_set['password'] = password
            up_set['salt'] = salt
        self.userdb.user.update(
            {'_id': uid},
            {'$set': up_set}
        )
