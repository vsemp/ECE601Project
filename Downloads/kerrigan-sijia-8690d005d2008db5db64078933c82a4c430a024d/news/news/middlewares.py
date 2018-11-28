# -*- coding: utf-8 -*-
import logging
import json
from selenium import webdriver
from scrapy.http import HtmlResponse
import random
import os

logger = logging.getLogger('middleware')


class InitHeaders(object):
    def process_request(self, request, spider):
        pass
        # if spider.need_headers:
        #     for k, v in spider.conf_headers.items():
        #         request.headers.setdefault(k, v)
        #     if spider.conf_cookies:
        #         request.cookies = spider.conf_cookies


class DomainDelay(object):
    def process_request(self, request, spider):
        request.meta['domain_delay'] = spider.get_domain_delay(request)


class InvalidHttpstatusDeal(object):
    def process_request(self, request, spider):
        request.meta['invalid_httpstatus_deal'] = spider.get_invalid_httpstatus_deal()


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        if 'noproxy' in request.meta:
            return None
        elif spider.cootek_proxy:
            request.meta['proxy'] = 'http://matrix03:9080?noconnect'
        elif spider.crius_proxy:
            request.meta['proxy'] = 'http://matrix03:9076?noconnect'
        elif spider.phoebe_proxy:
            request.meta['proxy'] = 'http://matrix03:9078?noconnect'
        elif spider.name == '7nujoom':
            request.meta['proxy'] = 'http://23.95.180.17:13228'
        elif spider.name.startswith('videoup'):
            ta = ['23.95.140.220:13228', '23.95.140.193:13228', '23.95.140.162:13228', '23.95.140.119:13228',
                  '23.95.140.111:13228', '23.95.140.22:13228', '23.95.139.115:13228', '23.95.139.93:13228',
                  '23.95.139.70:13228', '23.95.140.11:13228', '23.95.140.96:13228', '23.95.139.19:13228',
                  '198.23.195.16:13228', '192.210.248.207:13228', '192.210.248.100:13228', '192.210.248.86:13228',
                  '192.210.248.18:13228', '192.210.248.120:13228', '192.210.248.73:13228', '192.210.248.62:13228',
                  '198.23.195.104:13228', '198.23.195.47:13228',
                  '198.23.195.163:13228', '192.210.248.247:13228', '198.23.195.58:13228', ]
            request.meta['proxy'] = 'http://' + random.choice(ta)
        elif not spider.name.startswith('instagram'):
            ta = ['23.95.140.220:13228', '23.95.140.193:13228', '23.95.140.162:13228', '23.95.140.119:13228',
                  '23.95.140.111:13228', '23.95.140.22:13228', '23.95.139.115:13228', '23.95.139.93:13228',
                  '23.95.139.70:13228', '23.95.140.11:13228', '23.95.140.96:13228', '23.95.139.19:13228',
                  '198.23.195.16:13228', '192.210.248.207:13228', '192.210.248.100:13228', '192.210.248.86:13228',
                  '192.210.248.18:13228', '192.210.248.120:13228', '192.210.248.73:13228', '192.210.248.62:13228',
                  '198.23.195.104:13228', '198.23.195.47:13228',
                  '198.23.195.163:13228', '192.210.248.247:13228', '198.23.195.58:13228', ]
            request.meta['proxy'] = 'http://' + random.choice(ta)
        request.headers['domain_delay'] = json.dumps(spider.get_domain_delay(request))
        request.headers['invalid_httpstatus_deal'] = json.dumps(spider.get_invalid_httpstatus_deal())


class JavaScriptMiddleware(object):
    def process_request(self, request, spider):
        if spider.name in ["newrank"]:
            cwd = os.getcwd()
            phantom_path = os.path.join(os.getcwd(), 'tool/phantomjs-2.1.1-linux/bin/phantomjs')
            driver = webdriver.PhantomJS(executable_path=phantom_path)  # 指定使用的浏览器
            # driver = webdriver.Firefox()
            driver.get(request.url)
            js = "var q=document.documentElement.scrollTop=10000"
            driver.execute_script(js)  # 可执行js，模仿用户操作。此处为将页面拉至最底端。
            body = driver.page_source
            return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
        else:
            return
