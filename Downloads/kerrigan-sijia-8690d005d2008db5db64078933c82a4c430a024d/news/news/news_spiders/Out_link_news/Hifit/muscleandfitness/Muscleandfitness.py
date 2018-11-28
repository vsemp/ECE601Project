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
from selenium import webdriver
from .....spider_const import *
from ...out_link_news import OutLinkNews
import os

class MuscleandfitnessSpider(OutLinkNews):
    name = 'muscleandfitness'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'muscleandfitness'
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
        'http://muscleandfitness.com/nutrition/meal-plans/',
    ]

    def __init__(self, *a, **kw):
        super(MuscleandfitnessSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        parent_path = os.path.abspath(os.path.join(os.path.dirname('phantomjs-2.1.1-linux'), os.path.pardir))
        parent_path += '/news/news/news_spiders/phantomjs-2.1.1-linux/bin/phantomjs'
        driver = webdriver.PhantomJS(executable_path=parent_path)
        driver.get(response.url)
        selector = etree.HTML(driver.page_source)
        # print(etree.tostring(selector))

        urls = selector.xpath('//div/article/figure/div/div/div/div/div/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath('//div/article/figure/div/div/div/div/div/a/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        parent_path = os.path.abspath(os.path.join(os.path.dirname('phantomjs-2.1.1-linux'), os.path.pardir))
        parent_path += '/news/news/news_spiders/phantomjs-2.1.1-linux/bin/phantomjs'
        driver = webdriver.PhantomJS(executable_path=parent_path)
        driver.get(response.url)
        selector = etree.HTML(driver.page_source)
        try:
            raw['title'] = selector.xpath('//h1[@class="page-title b-node-full-title"]/span/text()')[0]
            raw['author'] = selector.xpath('//div[@class="b-node-full-author"]//span/a/text()')[0]
            raw['subtitle'] = ""
            raw['time'] = ''
            raw['tags'] = ['hifit_matrix']
            raw['source_name'] = 'muscleandfitness'
            raw['publisher'] = 'muscleandfitness'
            raw['keywords'] = []
            raw['subtitle'] = ''
            self.parse_raw(raw)

        except:
            logging.error('article fails to parse')


    def get_tags_from_raw(self, raw):
        return raw['tags']
