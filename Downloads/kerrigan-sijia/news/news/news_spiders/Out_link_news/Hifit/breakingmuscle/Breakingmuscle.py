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
from .....spider_const import *
from ...out_link_news import OutLinkNews


class BreakingmuscleSpider(OutLinkNews):
    name = 'breakingmuscle'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'breakingmuscle'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 1
    page_times = 0
    page_limit = 1
    content_list = []
    channel_list = [
        'http://breakingmuscle.com/healthy-eating/',
        'http://breakingmuscle.com/healthy-eating?page=2',
        'http://breakingmuscle.com/healthy-eating?page=3',
        'http://breakingmuscle.com/healthy-eating?page=4',
        'http://breakingmuscle.com/healthy-eating?page=5',

    ]

    def __init__(self, *a, **kw):
        super(BreakingmuscleSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        thumbnails = selector.xpath('//div[@id="content"]/div/div/div/a/img/@src')
        urls = selector.xpath('//div[@id="content"]/div/div/div/a/@href')
        title = selector.xpath('//div[@id="content"]/div/div/div/a/img/@title')
        author = selector.xpath('//div[@id="content"]/div/div/div/div/a/span/text()')
        for index, url in enumerate(urls):
            if self.is_source_url_exist(self.input_type, url):
                self.logger.info('source_url exists: ' + url)
            else:
                raw['thumbnails'] = [thumbnails[index]]
                raw['source_url'] = url
                raw['title'] = title[index]
                raw['author'] = author[index]
                raw['time'] = ''
                raw['tags'] = ['hifit_matrix']
                raw['source_name'] = 'breakingmuscle'
                raw['publisher'] = 'breakingmuscle'
                raw['keywords'] = []
                raw['subtitle'] = ''
                raw['author'] = ''
                self.parse_raw(raw)



                # self.content_list.append(copy.deepcopy(raw))

    def get_tags_from_raw(self, raw):
        return raw['tags']
