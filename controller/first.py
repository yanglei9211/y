#!/usr/bin/env python
# encoding: utf-8

from util.base_handler import BaseHandler
from debug_func import show_time_cost


class FirstHandler(BaseHandler):
    @show_time_cost
    def get(self):
        self.render(
            'first.html',
            name="123"
        )

    def post(self):
        dt = self.get_argument('data')
        print dt
        self.write({'res': dt})


class WelcomeHandler(BaseHandler):
    def get(self):
        self.render("welcome.html", user=self.current_user)
