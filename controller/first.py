#!/usr/bin/env python
# encoding: utf-8

from util.base_handler import BaseHandler
from app_define import USER_ROLE_TRANS

from util.decorator import show_time_cost


class FirstHandler(BaseHandler):
    @show_time_cost
    def get(self):
        name = self.get_argument('name', '')
        print name
        self.render(
            'first.html',
            name=name
        )

    def post(self):
        dt = self.get_argument('data')
        print dt
        self.write({'res': dt})


class WelcomeHandler(BaseHandler):
    def get(self):
        user = self.current_user
        user['role_str'] = USER_ROLE_TRANS[user['role']]
        self.render("welcome.html", user=user)
