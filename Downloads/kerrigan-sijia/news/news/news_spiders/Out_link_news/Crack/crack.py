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

from ..out_link_news import OutLinkNews
from ....spider_const import *


class CrackSpider(OutLinkNews):
    name = 'crack'
    source_name = 'crack'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'
          }

    browse_times = 0
    browse_limit = 2
    content_list = []
    channel_list = [
        'http://cracked.com/funny-articles.html/',
        'http://www.cracked.com/funny-articles_p2.html?date_year=2018&date_month=08',
        'http://www.cracked.com/funny-articles_p3.html?date_year=2018&date_month=08',
        'http://www.cracked.com/funny-articles_p4.html?date_year=2018&date_month=08',
    ]

    def __init__(self, *a, **kw):
        super(CrackSpider, self).__init__(*a, **kw)
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
        contents = selector.xpath('//div[@id="contentList"]/child::*')
        for content in contents:
            try:
                raw['source_url'] = content.xpath('.//a/@href')[0]
                if self.is_source_url_exist(self.input_type, raw['source_url']):
                    self.logger.info('source_url exists: ' + raw['source_url'])
                else:
                    raw['thumbnails'] = [content.xpath('.//a/@data-original')[0]]
                    raw['author'] = ''
                    raw['title'] = content.xpath('.//div/h3/a/text()')[0]
                    raw['subtitle'] = ''
                    # date = content.xpath('.//h4/time/@text()')[0]
                    raw['time'] = ''
                    raw['keywords'] = []
                    raw['tags'] = ['comedy']
                    raw['publisher'] = 'crack'
                    self.parse_raw(raw)

            except:
                logging.error("article fails to parse")

    def month_prepration(self, time):
        time_string = time.split(',')[1].strip()
        month = self.month_transfer(time.split(',')[0].split()[0])
        date = time.split(',')[0].split()[1]
        if len(date) == 2:
            time_string += '-' + month + '-' + date
        else:
            time_string += '-' + month + '-' + '0' + date
        return time_string

    def month_transfer(self, month):

        if month == 'Jan.' or month == 'January' or month == 'JANUARY':
            return '01'
        elif month == 'Feb.' or month == 'FEBRUARY' or month == 'February':
            return '02'
        elif month == 'Mar.' or month == 'MARCH' or month == 'March':
            return '03'
        elif month == 'Apr.' or month == 'APRIL' or month == 'April':
            return '04'
        elif month == 'May' or month == 'MAY' or month == 'May':
            return '05'
        elif month == 'June' or month == 'JUNE' or month == 'Jun':
            return '06'
        elif month == 'July' or month == 'JULY' or month == 'Jul':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST' or month == 'August':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER' or month == 'Sep' or month == 'September':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER' or month == 'October':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER' or month == 'November':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER' or month == 'December':
            return '12'
        else:
            logging.error('month parser failed')
