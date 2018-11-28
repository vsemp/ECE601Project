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


class SadanduselessSpider(OutLinkNews):
    name = 'sadanduseless'
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'sadanduseless'
    hd = {'pragma': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 2
    content_list = []
    channel_list = [
        'https://www.sadanduseless.com/',
        'https://www.sadanduseless.com/page/2/',
        'https://www.sadanduseless.com/page/3/',
        'https://www.sadanduseless.com/page/4/',
    ]

    def __init__(self, *a, **kw):
        super(SadanduselessSpider, self).__init__(*a, **kw)
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
            article_nodes = selector.xpath('//article')

            for article_node in article_nodes:
                thumbnails = article_node.xpath('.//div[@class="post-content"]/p[1]/a/img/@src')
                if thumbnails == []:
                    continue
                else:
                    raw['source_url'] = article_node.xpath('.//div[@class="post-content"]/p[1]/a/@href')[0]
                    if self.is_source_url_exist(self.input_type, raw['source_url']):
                        self.logger.info('source_url exists: ' + raw['source_url'])
                    else:
                        raw['thumbnails'] = [thumbnails[0]]
                        raw['author'] = ''
                        raw['title'] = \
                            article_node.xpath('.//header[@class="post-header "]/h2[@class="post-title"]/a/text()')[0]
                        raw['subtitle'] = ''
                        raw['time'] = ''
                        raw['keywords'] = []
                        raw['tags'] = ['comedy']
                        raw['publisher'] = 'sadanduseless'
                        self.parse_raw(raw)

        except:
            logging.error("the article fails to pass")
