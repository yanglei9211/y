#!/usr/bin/env python
# encoding: utf-8

import re
import bs4
import json
import time
import logging
import requests
import oss2

from util.service import Service
from util.file_util import save_oss
from bl.weibo import STATUS_TASK_CREATED
from bl.weibo import STATUS_TASK_DOING
from bl.weibo import STATUS_TASK_COMPLETED
from bl.weibo import STATUS_TASK_FAIL

cookie = "SINAGLOBAL=6927466390188.783.1490634914812; YF-Ugrow-G0=5b31332af1361e117ff29bb32e4d8439; TC-V5-G0=5fc1edb622413480f88ccd36a41ee587; _s_tentry=login.sina.com.cn; Apache=4466225828739.979.1496078171620; TC-Page-G0=fd45e036f9ddd1e4f41a892898506007; ULV=1496078172219:7:3:1:4466225828739.979.1496078171620:1494674087810; TC-Ugrow-G0=370f21725a3b0b57d0baaf8dd6f16a18; login_sid_t=251d1e666bb97fd07ec57361f73a247f; wb_cmtLike_1688817625=1; UOR=,,login.sina.com.cn; WBtopGlobal_register_version=70c17b055422a67b; SSOLoginState=1501249939; un=80871930@qq.com; wvr=6; SCF=Am1Ojg6oClQVIdWbBoPkQaGWZFTWGvh-Fu8VRFyIBrVCy6Lqw2OTZW8RsMCvDGxAP1-qELzRzvLdy-eceTtWDsQ.; SUB=_2A250eRJUDeThGedI41oZ8SnKyTmIHXVXDwScrDV8PUJbmtAKLWrwkW8AXiwFofd9PrZmlyYiqmjDZfiwtg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFAbArjHPiRaHRwJK79riRS5JpX5o2p5NHD95QpSonR1h2NSozfWs4DqcjzxcHaMsHjIg2t; SUHB=0XD0K7Yy5ilQOk; ALF=1532785939"
header = {
'Connection': 'keep-alive',
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Cookie': cookie}

del_af = re.compile(ur"<a.*?>")
del_ae = re.compile(ur"</a>")
del_em = re.compile(ur"<em.*?</em>")
del_i = re.compile(ur"<i.*?</i>")
search_img_title = re.compile(ur"title=\"(.*?)\"")


def filter_text(tag_name, tag):

    if tag_name == "img":
        res = unicode(tag)
        r = search_img_title.search(res)
        res = r.group(1) if r else ""
    else:
        res = unicode(tag)
        res = del_af.subn("", res)[0]
        res = del_ae.subn("", res)[0]
        res = del_em.subn("", res)[0]
        res = del_i.subn("", res)[0]

    return res


def get_comment(rid, page, ans):
    url = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&filter=all&page=%d' % (rid, page)
    res = requests.get(url, headers=header)
    dt = json.loads(res.content)
    soup = bs4.BeautifulSoup(dt['data']['html'], "html.parser")
    reslist = soup.findAll('div', attrs={'class': 'WB_text'})
    for r in reslist:
        rp = ""
        for c in r.children:
            add = filter_text(c.name, c)
            rp += add if add != "\n" else ""
        ans.append(rp)
        # s = u""
        # for c in r.children:
        #     s += unicode(c)
        # print "-" * 23
        # s = del_af.subn("", s)[0]
        # s = del_ae.subn("", s)[0]
        # print s
    return len(reslist) > 0


def get_comments_by_rid(rid):
    page = 1
    ans = []
    while get_comment(rid, page, ans):
        page += 1
    res_str = ""
    for s in ans:
        res_str += s + "\n"
    return res_str


def get_weibo_id(url):
    res = requests.get(url, headers=header)
    rid = re.search(ur"rid=(\d+)\&", res.content)
    return rid.group(1) if rid else None


class PeriodService(Service):
    def main(self):
        logging.info("try to get task")
        task = self.db.task.find_and_modify({'status': STATUS_TASK_CREATED},
                                            {'$set': {'status': STATUS_TASK_DOING}})

        try:
            if task:
                logging.info("get task: %s, rid: %s" % (task['_id'], task['data']))
                task_type = task['type']
                rid = task['data'] if task_type == "rid" else get_weibo_id(task['data'])
                res_str = get_comments_by_rid(rid)
                res_str = res_str.encode("utf-8")
                file_name = save_oss(self.oss_bucket, "doc", res_str, "txt")
                self.db.task.update({'_id': task['_id']},
                                    {'$set': {'status': STATUS_TASK_COMPLETED,
                                              'file_name': file_name,
                                              'mtime': time.time()}})
        except Exception as e:
            logging.error(e)
            self.db.task.update({'_id': task['_id']},
                                {'$set': {'status': STATUS_TASK_FAIL,
                                          'mtime': time.time()}})

if __name__ == "__main__":
    PeriodService(3).run()
