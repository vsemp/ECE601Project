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


class EliteftsSpider(OutLinkNews):
    name = 'elitefts'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'elitefts'
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
        'http://elitefts.com/education/nutrition//',
        'https://www.elitefts.com/education/nutrition/page/2/',
        'https://www.elitefts.com/education/nutrition/page/3/',
    ]

    def __init__(self, *a, **kw):
        super(EliteftsSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        urls = selector.xpath(
            '//ul[contains(@class,"post-list-row")]/li/div[@class="post-list-item"]/div[@class="featured-image"]/a/@href')
        title = selector.xpath(
            '//ul[contains(@class,"post-list-row")]/li/div[@class="post-list-item"]/div[@class="featured-image"]/a/@title')
        thumbnails = selector.xpath(
            '//ul[contains(@class,"post-list-row")]/li/div[@class="post-list-item"]/div/a/img/@data-src')
        time = selector.xpath('//p[@class="post-date"]/text()')
        author_raw = selector.xpath('//p[@class="post-author"]/a')
        # print('11', urls, len(title), thumbnails, len(time), len(author_raw))
        for index, url in enumerate(urls):
            if self.is_source_url_exist(self.input_type, url):
                self.logger.info('source_url exists: ' + url)
            else:
                raw['source_url'] = url
                raw['thumbnails'] = [thumbnails[index]]
                raw['subtitle'] = ''
                raw['title'] = title[index]
                author = etree.tostring(author_raw[index], method='html', with_tail=False)
                author = re.sub('<[^>]*>', '', author)
                raw['author'] = author.strip()
                year = time[index].split(',')[1]
                date = time[index].split(',')[0].split(' ')[1]
                month = time[index].split(',')[0].split(' ')[0]
                # print('22', year, date, month)
                month = self.month_transfer(month)
                # print('11', year, date, month)
                time_raw = year + '-' + month + '-' + date
                raw['time'] = time_raw.strip()
                # print(raw['source_url'])
                # print(raw['thumbnails'])
                # print(raw['author'])
                # print(raw['time'])
                raw['tags'] = ['hifit_matrix']
                raw['source_name'] = 'elitefts'
                raw['publisher'] = 'elitefts'
                raw['keywords'] = []
                self.parse_raw(raw)

    def month_transfer(self, month):
        if month == 'Jan.' or month == 'January' or month == 'Jan':
            return '01'
        elif month == 'Feb.' or month == 'FEBRUARY' or month == 'Feb':
            return '02'
        elif month == 'Mar.' or month == 'MARCH' or month == 'Mar':
            return '03'
        elif month == 'Apr.' or month == 'APRIL' or month == 'Apr':
            return '04'
        elif month == 'May' or month == 'MAY':
            return '05'
        elif month == 'June' or month == 'JUNE' or month == 'Jun':
            return '06'
        elif month == 'July' or month == 'JULY' or month == 'Jul':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST' or month == 'Aug':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER' or month == 'Sep':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER' or month == 'Oct':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER' or month == 'Nov':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER' or month == 'Dec':
            return '12'
        else:
            logging.error('month parser failed')

    def get_tags_from_raw(self, raw):
        return raw['tags']
