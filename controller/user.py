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
from bl.user import get_all_user
from errors import BLError
from app_define import USER_ROLE_FULL, USER_ROLE_PARTIAL
from app_define import USER_ROLE_TRANS

# TODO 权限组管理


class ListHandler(BaseHandler):
    def get(self):
        users = get_all_user(self)
        for user in users:
            user['role_str'] = USER_ROLE_TRANS[user['role']]
        self.render(
            'user/list.html',
            users=users
        )


class AccountHandler(BaseHandler):

    def get(self):
        user = self.get_current_user()
        if user is None:
            raise HTTPError(404, "no current user")
        user['role_str'] = USER_ROLE_TRANS[user['role']]
        self.render(
            'user/account.html',
            user=user
        )

    def post(self):
        if options.debug:
            self.write({})
            return
        user = self.userdb.user.find_one({'username': self.m})
        assert user is not None
        name = self.get_argument('name')
        assert_name_legal(name)
        up_set = {
            'name': name
        }
        current_pwd = self.get_argument('cpwd', '')
        new_pwd = self.get_argument('npwd', '')
        if current_pwd or new_pwd:
            if hash_pwd(current_pwd, user['salt']) != user['password']:
                raise BLError(u"当前密码错误")
            salt = gen_salt()
            password = hash_pwd(new_pwd, salt)
            up_set['salt'] = salt
            up_set['password'] = password
        self.userdb.user.update(
            {'_id': user['_id']},
            {'$set': up_set}
        )
        self.write({})


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

    def post(self, uid=None):
        action = self.get_argument('action')
        if uid:
            uid = safe_objectid_from_str(uid)
        else:
            raise HTTPError(400, "no user id")
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
        valid_status = not user['valid']
        self.userdb.user.update(
            {'_id': uid},
            {'$set': {'valid': valid_status}}
        )
        logging.info("user id:{}  username:{}  status change into {} by {}".format(
            user['_id'], user['username'], valid_status, self.m
        ))

    def create(self):
        username = self.get_argument('username')
        assert_username_legal(username)
        name = self.get_argument('name')
        assert_name_legal(name)
        password = self.get_argument('password')
        role = self.get_argument('role', type_=int)
        user = create_user(self, username, name, password, role)
        try:
            self.userdb.user.insert(user)
        except:
            raise BLError(u'用户名已存在')

    def save(self, uid):
        name = self.get_argument('name')
        assert_name_legal(name)
        password = self.get_argument('password', '')
        role = self.get_argument('role', type_=int)
        up_set = {
            'name': name,
            'role': role,
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
            return "/main"


class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie('user', domain=self.get_main_domain())
        self.clear_cookie('login_sn', domain=self.get_main_domain())
        # 跳回等出前的界面
        self.redirect(self.request.headers.get('Referer', '/'))