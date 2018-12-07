# -*- coding: utf-8 -*-

import scrapy
import copy
import re
import time
import json
import copy
import scrapy
from scrapy import signals
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
import requests
import lxml
from lxml import etree
import traceback
import pprint
import logging
import base64
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium import webdriver

from ..out_link_news import OutLinkNews
from ....spider_const import *


class MemecenterSpider(OutLinkNews):
    name = 'memecenter'
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'memecenter'
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 2
    content_list = []
    channel_list = ['http://memecenter.com/', ]

    def __init__(self, *a, **kw):
        super(MemecenterSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):

        if self.browse_times <= self.browse_limit and self.channel_list:
            self.browse_times += 1
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        channel_url = self.channel_list.pop()

        raw = dict()
        raw['inlinks'] = [channel_url]
        yield Request(
            url=channel_url,
            meta=raw,
            headers=self.hd,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)

        # driver = webdriver.PhantomJS(executable_path='/Users/zheyiyi/Desktop/touchpal/phantomjs-2.1.1-macosx/bin/phantomjs')
        # driver.get(response.url)

        # for i in range(1,15):
        #	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #	time.sleep(3)

        selector = etree.HTML(response.body)

        contents = selector.xpath('//div[@class="content  "]')

        for content in contents:
            try:
                raw['source_url'] = content.xpath('.//div[@class="content-title"]/h2/a/@href')[0]
                if self.is_source_url_exist(self.input_type, raw['source_url']):
                    self.logger.info('source_url exists: ' + raw['source_url'])
                else:
                    raw['thumbnails'] = [content.xpath('.//div/a/img/@src')[0]]
                    raw['author'] = content.xpath('.//div/div[@class="content-user"]/div/a/text()')[0]
                    raw['title'] = content.xpath('.//div/div[@class="content-title"]/h2/a/text()')[0]
                    raw['subtitle'] = ''
                    raw['time'] = content.xpath('.//div/div[@class="content-featured"]/abbr/@datetime')[0].split('T')[0]
                    raw['keywords'] = []
                    raw['tags'] = ['comedy']
                    raw['publisher'] = 'memecenter'
                    self.parse_raw(raw)
            except:
                logging.error('article fails to parse')
