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
from app_define import USER_ROLE_FULL, USER_ROLE_PARTIAL


class UserHandler(BaseHandler):

    def get(self, uid=None):
        if uid:
            uid = safe_objectid_from_str(uid)
            user = fetch_user(self, uid)
        else:
            user = None

        self.render(
            'user/form.html',
            user=user,
            roles={
                USER_ROLE_FULL: u'全职',
                USER_ROLE_PARTIAL: u'兼职'
            }
        )

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


class LoginHandler(BaseHandler):
    allow_anony = True

    def get(self):
        if self.current_user is not None:
            self.redirect(self.get_next_url())
        else:
            self.render("user/login.html",
                        rand_num=int(random.random() * 10)+1)

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        user = self.userdb.user.find_one({'username': username})
        if user is None:
            raise BLError(u'用户不存在')
        if not user['valid']:
            raise BLError(u'用户不可用')

        if hash_pwd(password, user['salt']) != user['password']:
            raise BLError(u'密码错误')
        self.userdb.user.update({'username': username},
                                {'$set': {'last_login_time': time.time()}})

        cookie_user = {
            'username': username,
            'login_sn': gen_salt(),
        }
        print self.get_main_domain()
        self.set_secure_cookie(
            'user',
            self.dumps(cookie_user),
            domain=self.get_main_domain()
        )

        self.set_cookie(
            'login_sn',
            cookie_user['login_sn'],
            domain=self.get_main_domain(),
        )

        self.write({'url': self.get_next_url()})

    def get_next_url(self):
        referer = self.request.headers.get('Referer')
        # 用来实现,访问某界面,跳转登陆界面,登陆后跳回之前的界面?
        if referer and referer != self.request.full_url():
            return referer
        else:
            return "/test/local/file"
