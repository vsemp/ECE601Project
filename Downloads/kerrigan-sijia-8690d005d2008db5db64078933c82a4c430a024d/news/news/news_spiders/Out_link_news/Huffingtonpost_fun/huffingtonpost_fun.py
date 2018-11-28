# -*- coding: utf-8 -*-


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


class Huffingtonpost_fun_Spider(OutLinkNews):
    name = 'huffingtonpost'
    source_name = 'huffingtonpost'
    egion = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    download_delay = 3
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
    channel_list = ['https://www.huffingtonpost.com/topic/funny', 'https://www.huffingtonpost.com/topic/funny?page=2',
                    'https://www.huffingtonpost.com/topic/funny?page=3',
                    'https://www.huffingtonpost.com/topic/funny?page=4',
                    'https://www.huffingtonpost.com/topic/funny?page=5',
                    'https://www.huffingtonpost.com/topic/funny?page=6', ]

    def __init__(self, *a, **kw):
        super(Huffingtonpost_fun_Spider, self).__init__(*a, **kw)
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
        # try:
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        article_nodes = selector.xpath('//div[@class="zone__content"]/child::*')
        for article_node in article_nodes:
            thumbnails = article_node.xpath('.//div/a/div/img/@src')
            if not thumbnails:
                continue
            else:
                if 'VIDEOS' not in article_node.xpath('.//div/div/div/span/text()')[0]:
                    raw['source_url'] = response.urljoin(article_node.xpath('.//div/div/div/a/@href')[0])
                    if self.is_source_url_exist(self.input_type, raw['source_url']):
                        self.logger.info('source_url exists: ' + raw['source_url'])
                    else:
                        raw['thumbnails'] = [article_node.xpath('.//div/a/div/img/@src')]
                        raw['author'] = ''
                        raw['title'] = article_node.xpath('.//div/div/div/div/a/div/text()')[0]
                        raw['subtitle'] = article_node.xpath('.//div/div/div/div/a/text()')[0]
                        raw['time'] = ''
                        raw['keywords'] = []
                        raw['tags'] = ['comedy']
                        raw['publisher'] = 'huffingtonpost'
                        self.parse_raw(raw)
                    # except:
                    #	logging.error("this article fails to scrapy")
