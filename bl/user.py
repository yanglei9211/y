#!/usr/bin/env python
# encoding: utf-8

import time
import random
import string
import hashlib
import re

from errors import BLError
from app_define import USER_ROLE_MANAGER


def hash_pwd(pwd, salt):
    return hashlib.sha1(pwd + '|' + salt).hexdigest()[:16]


def gen_salt():
    return ''.join(random.choice(string.letters) for i in xrange(16))


def create(handler, username, name, password):
    salt = gen_salt()
    password = hash_pwd(password, salt)
    return {
        'username': username,
        'name': name,
        'password': password,
        'salt': salt,
        'valid': True,
        'ctime': time.time(),
        'creator': handler.m,
    }


def fetch_user(handler, uid):
    user = handler.userdb.user.find_one({'_id': uid})
    if not user:
        raise BLError(u'用户不存在')
    return user


def assert_username_legal(username):
    if not re.match(ur'^[A-Za-z0-9]{4,20}$', username):
        raise BLError(u'用户名不合法,要求4-20位,只包含小写字母和数字')


def assert_name_legal(name):
    if not re.match(ur'^[\u4E00-\u9FA5a-zA-Z0-9]{1,20}$', name):
        raise BLError(u'姓名不合法,要求1-20个字符,只包含中文,大小写字母,数字')
