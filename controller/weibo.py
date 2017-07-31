#!/usr/bin/env python
# encoding: utf-8

from tornado.web import HTTPError
from tornado.options import options

from util.base_handler import BaseHandler
from util.authorization import ManagerHandler
from util.escape import safe_objectid_from_str
from util.common import Pager
from bl.weibo import create_task


class WeiboHandler(ManagerHandler):
    def get(self):
        cursor = self.db.task.find({}, sort=[('_id', -1)])
        pager = Pager(self)
        cursor = pager.paginate(cursor)
        page_data = pager.paged_response()
        # tasks = list(self.db.task.find({}, sort=[('_id', -1)]))
        tasks = list(cursor)
        self.render("weibo/task.html", tasks=tasks, page=page_data,
                    oss_pre="http://erich.oss-cn-beijing.aliyuncs.com")

    def post(self):
        action = self.get_argument('action')
        res_data = 0
        if action == "url":
            wb_url = self.get_argument('wb_url')
            create_task(self, action, wb_url)
        elif action == "rid":
            wb_rid = self.get_argument("wb_rid")
            create_task(self, action, wb_rid)
        else:
            raise HTTPError(400)
        self.write({})
