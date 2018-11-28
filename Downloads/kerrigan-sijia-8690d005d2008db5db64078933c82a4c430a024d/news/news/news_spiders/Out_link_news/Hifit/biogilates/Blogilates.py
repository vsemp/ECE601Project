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


class BlogilatesSpider(OutLinkNews):
    name = 'blogilates'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'blogilates'
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
    channel_list = ['http://www.blogilates.com/category/food-2/',
                    'http://www.blogilates.com/category/food-2/page/2/',
                    'http://www.blogilates.com/category/food-2/page/3/',
                    'http://www.blogilates.com/category/food-2/page/4/',
                    'http://www.blogilates.com/food/',
                    'http://www.blogilates.com/food/page/2/',
                    'http://www.blogilates.com/food/page/3/',
                    'http://www.blogilates.com/food/page/4/',
                    ]

    def __init__(self, *a, **kw):
        super(BlogilatesSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        # print(etree.tostring(selector))
        if 'https://www.blogilates.com/category' not in raw['inlinks'][0]:
            thumbnails = selector.xpath('//ul/li[@class="col span_4"]/a/div/a/img/@data-lazy-src')
            urls = selector.xpath('//ul/li[@class="col span_4"]/a/@href')
            titles = selector.xpath('//ul/li[@class="col span_4"]/a/h4/text()')
            # print(len(urls), len(thumbnails), len(titles))
            for index, url in enumerate(urls):
                raw['thumbnails'] = [thumbnails[index]]
                raw['source_url'] = url
                raw['title'] = titles[index]
                raw['tags'] = ['hifit_matrix']
                raw['author'] = ''
                raw['time'] = ''
                raw['source_name'] = 'blogilates'
                raw['publisher'] = 'blogilates'
                raw['keywords'] = []
                raw['subtitle'] = ''
                self.parse_raw(raw)
        # print(raw['source_url'],raw['thumbnails'],'11')
        # self.content_list.append(copy.deepcopy(raw))
        else:
            thumbnails = selector.xpath('//article/div/a/img/@data-lazy-src')
            urls = selector.xpath('//article/div/a/@href')
            titles = selector.xpath('//article/div/div/div/h3/a/text()')
            time = selector.xpath('//article/div/div/div/span/text()')
            for index, url in enumerate(urls):
                if self.is_source_url_exist(self.input_type, url):
                    self.logger.info('source_url exists: ' + url)
                else:
                    raw['thumbnails'] = [thumbnails[index]]
                    raw['title'] = titles[index]
                    year = time[index].split(',')[1].strip()
                    date = time[index].split(',')[0].split(' ')[1].strip()
                    month = time[index].split(',')[0].split(' ')[0].strip()
                    # print('22', year, date, month)
                    month = self.month_transfer(month)
                    # print('11', year, date, month)
                    time_raw = year + '-' + month + '-' + date
                    raw['time'] = time_raw.strip()
                    raw['source_url'] = url
                    # print(raw['title'],raw['source_url'],raw['thumbnails'],raw['time'])
                    raw['tags'] = ['hifit_matrix']
                    raw['source_name'] = 'blogilates'
                    raw['publisher'] = 'blogilates'
                    raw['keywords'] = []
                    raw['subtitle'] = ''
                    raw['author'] = ''
                    self.parse_raw(raw)


                # print(raw['thumbnails'])
                # self.content_list.append(copy.deepcopy(raw))

    def month_transfer(self, month):
        if month == 'Jan.' or month == 'January' or month == 'Jan' or month == 'January':
            return '01'
        elif month == 'Feb.' or month == 'FEBRUARY' or month == 'Feb' or month == 'February':
            return '02'
        elif month == 'Mar.' or month == 'MARCH' or month == 'Mar' or month == 'March':
            return '03'
        elif month == 'Apr.' or month == 'APRIL' or month == 'Apr' or month == 'April':
            return '04'
        elif month == 'May' or month == 'MAY' or month == 'May':
            return '05'
        elif month == 'June' or month == 'JUNE' or month == 'Jun' or month == 'June':
            return '06'
        elif month == 'July' or month == 'JULY' or month == 'Jul' or month == 'July':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST' or month == 'Aug' or month == 'August':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER' or month == 'Sep' or month == 'September':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER' or month == 'Oct' or month == 'October':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER' or month == 'Nov' or month == 'November':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER' or month == 'Dec' or month == 'December':
            return '12'
        else:
            logging.error('month parser failed')

    def get_tags_from_raw(self, raw):
        return raw['tags']
