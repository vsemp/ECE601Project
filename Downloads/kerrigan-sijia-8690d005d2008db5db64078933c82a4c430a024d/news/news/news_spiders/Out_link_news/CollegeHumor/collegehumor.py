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


class CollegeHumorSpider(OutLinkNews):
    name = 'collegeHumor'
    download_delay = 3
    source_name = 'collegeHumor'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    datasource_type = 2
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
        'http://collegehumor.com/articles/',
        'http://www.collegehumor.com/articles/page:2',
        'http://www.collegehumor.com/articles/page:3'

    ]

    def __init__(self, *a, **kw):
        super(CollegeHumorSpider, self).__init__(*a, **kw)
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

        selector = etree.HTML(response.body)
        try:

            urls = selector.xpath('//li[@class="listing-section__list-item"]/a/@href')
            urls = [response.urljoin(url) for url in urls]
            titles = selector.xpath('//li[@class="listing-section__list-item"]/a/div/h4/text()')
            thumbnails = selector.xpath('//li[@class="listing-section__list-item"]/a/img/@data-src')

            for index, url in enumerate(urls):
                if 'video' not in url:
                    raw['source_url'] = url
                    if self.is_source_url_exist(self.input_type, raw['source_url']):
                        self.logger.info('source_url exists: ' + raw['source_url'])
                    else:
                        raw['thumbnails'] = [thumbnails[index]]
                        raw['author'] = ''
                        raw['title'] = titles[index]
                        raw['subtitle'] = ''
                        raw['time'] = ''
                        raw['keywords'] = []
                        raw['tags'] = ['comedy']
                        raw['publisher'] = 'collegehumor'
                        self.parse_raw(raw)

        except:
            logging.error("the article fails to parse")

