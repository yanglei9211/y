#!/usr/bin/env python
# encoding: utf-8

import re
import json
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

from util.service import Service


cookie = 'cdkey=; account=y80871930; as=0; al=1; grabcodestatus=3; UM_distinctid=15c0f1c0de4ed5-072fdace29a3fe-39687804-1fa400-15c0f1c0de5fe1; PHPSESSID=36cb143d12986ea9bd171121fce43f32; __ozlvd751=1503898464; Hm_lvt_81e08fa486e18ee1201ac0857d1b1ddf=1509342446; Hm_lpvt_81e08fa486e18ee1201ac0857d1b1ddf=1509342662; OZ_SI_751=sTime=1503898418&sIndex=31; OZ_1U_751=vid=v9a3ab33e9e9dd.0&ctime=1509680619&ltime=1509680613; OZ_1Y_751=erefer=https%3A//www.baidu.com/link%3Furl%3DLQ02Bu4TzSG-Ncka2NzNnd7goAdEeJsHjPl5gEF-sMe%26wd%3D%26eqid%3Dc49e7c26000009b20000000559fbe5e2&eurl=http%3A//jx3.xoyo.com/&etime=1509680613&ctime=1509680619&ltime=1509680613&compid=751; CNZZDATA30050295=cnzz_eid%3D1810881775-1494901198-null%26ntime%3D1509955376; CNZZDATA30048117=cnzz_eid%3D760925311-1494897450-null%26ntime%3D1509953689; Hm_lvt_6a4bf253106aa865402b86b2ae40d3bc=1509342505,1509528647,1509595342,1509680614; Hm_lpvt_6a4bf253106aa865402b86b2ae40d3bc=1509955859; session_id=246469eff28fb1de018ed55b23b40ea8507b0f20; xoyokey=Ik%2F%2Fr3TTZ1ffDy3G%3DffHD-y%26%261Zz3n%3D%26nzc3L%3Dxy55H..%2F%261%2Fm%2F%2FxH5fDmzn-zD%26H5mKmT%26K3YxDn5-c.0-%3Dm%3D5mZEm-m%2FEH%26%2Fcl-%26'
headers = {
    'Connection': 'keep-alive',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cookie': cookie
}
url = 'http://jx3.xoyo.com/zt/2017/08/28/getcode/index.html'

from debug_func import show_time_cost

class PeriodService(Service):
    def get_hearders_driver(self):
        desire = DesiredCapabilities.PHANTOMJS.copy()
        for key, value in headers.iteritems():
            desire['phantomjs.page.customHeaders.{}'.format(key)] = value
        driver = webdriver.PhantomJS(desired_capabilities=desire,
                                     service_args=['--load-images=yes'])  # 将yes改成no可以让浏览器不加载图片
        return driver
    @show_time_cost
    def main(self):
        driver = self.get_hearders_driver()
        driver.get(url)
        driver.find_element_by_id('key_apply').click()
        # sss = re.findall(ur"win_dialog", driver.page_source)
        res = driver.find_element_by_id('win_dialog').text
        driver.refresh()
        cur = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print cur
        print res


if __name__ == "__main__":
    PeriodService(1).run()
