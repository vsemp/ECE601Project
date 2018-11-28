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
from ..out_link_news import OutLinkNews
from ....spider_const import *


class NbcSpider(OutLinkNews):
    name = 'nbc'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'nbc'
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
        'http://nbcnews.com/',
    ]

    def __init__(self, *a, **kw):
        super(NbcSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        # print(etree.tostring(selector))
        urls = selector.xpath('//div[@class="taboola-cover-us-news-textlink"]/div/div/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath('//div[@class="taboola-cover-us-news-textlink"]/div/div/a/noscript/img/@src')
        # print('111', len(urls), len(thumbnails))
        # print('22', urls, thumbnails)

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="col-md-6 curated-list_item"]/div[@class="story-link story-link_sm story-link_media"]/div[@class="img-container img-container_media img-container_storylink"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="col-md-6 curated-list_item"]/div[@class="story-link story-link_sm story-link_media"]/div[@class="img-container img-container_media img-container_storylink"]/a/noscript/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div/div[@class="story-link story-link_sm"]/div[@class="img-container img-container_default visible-xs-block visible-sm-block"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div/div[@class="story-link story-link_sm"]/div[@class="img-container img-container_default visible-xs-block visible-sm-block"]/a/noscript/img/@src')
        # print('333', len(urls), len(thumbnails))
        # print('444', urls)
        # print('555', thumbnails)
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        try:
            raw.update(response.meta)
            selector = etree.HTML(response.body)
            if raw['thumbnails'] == []:
                pass
            else:
                title = selector.xpath(
                    '//h1[@class="headline___CuovH f8 f9-m fw3 mb3 mt0 founders-cond lh-none f10-xl"]/text()')
                raw['title'] = title[0]
                print(title)
                author_elm = selector.xpath('//span[@class="inlineAuthor___sgwQx"]')[0]
                author = re.sub('<[^>]*>', '', etree.tostring(author_elm, method='html', with_tail=False))
                raw['author'] = author.strip().replace('/', '').strip()
                print(raw['author'])
                time = selector.xpath('//time[@class="pubDate___3OViw"]/text()')[0].split('/')[0].strip()
                new_string = time.split('.')[2]
                month = self.month_transfer(time.split('.')[0])
                date = time.split('.')[1]

                if len(date) == 2:
                    new_string += '-' + month + '-' + date
                else:
                    new_string += '-' + month + '-' + '0' + date
                raw['time'] = new_string
                print(raw['time'])

                raw['keywords'] = []
                raw['tags'] = []
                raw['publisher'] = 'npr'
                raw['subtitle'] = ''
                self.parse_raw(raw)

        except:
            logging.error("this article fails to scrapy")

    def month_transfer(self, month):

        if month == 'Jan.' or month == 'January':
            return '01'
        elif month == 'Feb.' or month == 'FEBRUARY':
            return '02'
        elif month == 'Mar.' or month == 'MARCH':
            return '03'
        elif month == 'Apr.' or month == 'APRIL':
            return '04'
        elif month == 'May' or month == 'MAY':
            return '05'
        elif month == 'June' or month == 'JUNE' or month == 'Jun':
            return '06'
        elif month == 'July' or month == 'JULY' or month == 'Jul':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER' or month == 'Sep':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER':
            return '12'
        else:
            logging.error('month parser failed')
