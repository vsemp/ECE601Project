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


class NprSpider(OutLinkNews):
    name = 'npr'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'npr'
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
        'http://npr.org/',
    ]

    def __init__(self, *a, **kw):
        super(NprSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        #print(etree.tostring(selector))
        urls = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-featured"]/article[@class="hp-item volume-low post-type-standard has-image "]/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/@href')
        thumbnails = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-featured"]/article[@class="hp-item volume-low post-type-standard has-image "]/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-featured"]/section[@class="featured-group"]/article/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/@href')
        thumbnails = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-featured"]/section[@class="featured-group"]/article/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-two"]/article/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/@href')
        thumbnails = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-two"]/article/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-two"]/section[@class="attachment-group"]/article[@class="hp-item volume-low post-type-standard has-attachment has-image "]/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/@href')
        thumbnails = selector.xpath(
            '//div[@class="stories-wrap stories-wrap-two"]/section[@class="attachment-group"]/article[@class="hp-item volume-low post-type-standard has-attachment has-image "]/div[@class="story-wrap"]/figure[@class="thumb-image"]/div[@class="bucketwrap homeThumb"]/div[@class="imagewrap"]/a/img/@src')

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
                raw['title'] = selector.xpath('//h1/text()')[0]

                if selector.xpath('//a[@rel="author"]/text()') == []:
                    raw['author'] = selector.xpath('//p[@class="byline__name byline__name--block"]/text()')[0].strip()
                else:
                    raw['author'] = selector.xpath('//a[@rel="author"]/text()')[0].strip()

                new_string = selector.xpath('//time/span[@class="date"]/text()')[0].split(',')[1].strip()
                month = self.month_transfer(
                    selector.xpath('//time/span[@class="date"]/text()')[0].split(',')[0].split(' ')[0].strip())
                date = selector.xpath('//time/span[@class="date"]/text()')[0].split(',')[0].split(' ')[1].strip()

                if len(date) == 2:
                    new_string += '-' + month + '-' + date
                else:
                    new_string += '-' + month + '-' + '0' + date
                raw['time'] = new_string
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
        elif month == 'June' or month == 'JUNE':
            return '06'
        elif month == 'July' or month == 'JULY':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER':
            return '12'
        else:
            logging.error('month parser failed')













