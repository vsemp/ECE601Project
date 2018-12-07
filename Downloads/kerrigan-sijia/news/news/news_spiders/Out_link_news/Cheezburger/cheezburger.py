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


class CheezburgerSpider(OutLinkNews):
    name = 'cheezburger'
    download_delay = 3
    datasource_type = 2
    source_name = 'cheezburger'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 2
    content_list = []
    channel_list = [
        'http://cheezburger.com/',
        'https://www.cheezburger.com/page/2',
        'https://www.cheezburger.com/page/3',
        'https://www.cheezburger.com/page/5',

    ]

    def __init__(self, *a, **kw):
        super(CheezburgerSpider, self).__init__(*a, **kw)
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
        try:
            raw.update(response.meta)
            selector = etree.HTML(response.body)
            json_docs = selector.xpath('//div[@class="content-card "]/div[@class="nw-post   js-post"]/@data-model')

            for json_doc in json_docs:
                # print(json_doc,'11')
                json_doc = json.loads(json_doc)
                if 'gif' not in json_doc['Url']:
                    raw['source_url'] = json_doc["CanonicalUrl"]
                    if self.is_source_url_exist(self.input_type, raw['source_url']):
                        self.logger.info('source_url exists: ' + raw['source_url'])
                    else:
                        raw['title'] = json_doc["Title"]
                        raw['thumbnails'] = [json_doc['Url']]
                        raw['author'] = ''
                        raw['subtitle'] = ''
                        raw['time'] = ''
                        raw['keywords'] = []
                        raw['tags'] = ['comedy']
                        raw['publisher'] = 'cheezburger'
                        self.parse_raw(raw)
        except:
            logging.error("the article fails to pass")
