#!/usr/bin/env python
# encoding: utf-8

import time

STATUS_TASK_CREATED = 0
STATUS_TASK_DOING = 1
STATUS_TASK_COMPLETED = 2
STATUS_TASK_FAIL = -1


def create_task(handler, action, data):
    cur_time = time.time()
    task = {
        'type': action,
        'data': data,
        'status': STATUS_TASK_CREATED,
        'ctime': cur_time,
        'mtime': cur_time,
    }
    handler.db.task.insert(task)
