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


class PoliticoSpider(OutLinkNews):
    name = 'politico'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'politico'
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
        'http://politico.com/',
    ]

    def __init__(self, *a, **kw):
        super(PoliticoSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)

        selector = etree.HTML(response.body)
        # print(etree.tostring(selector))
        # with open('html.txt','w') as fh:
        #	fh.write(etree.tostring(selector))
        urls = selector.xpath(
            '//section[@class="media-item "]/div[@class="media-item__image"]/div[@class="media-item__image-wrapper"]/a[@target="_blank"]/@href')
        thumbnails = selector.xpath(
            '//section[@class="media-item "]/div[@class="media-item__image"]/div[@class="media-item__image-wrapper"]/a[@target="_blank"]/picture/source/source/source/source/source/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="module module-layout--50-50 "]/div[@class="module__column"]/section[@class="media-item "]/div/div/a/@href')
        thumbnails = selector.xpath(
            '//div[@class="module module-layout--50-50 "]/div[@class="module__column"]/section[@class="media-item "]/div/div/a/picture/source/source/source/source/source/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="module  has-bottom-divider"]/section[@class="media-item orient--horizontal-50-50-dual-summary "]/div[@class="media-item__group"]/div[@class="media-item__image"]/div/a/@href')
        thumbnails = selector.xpath(
            '//div[@class="module  has-bottom-divider"]/section[@class="media-item orient--horizontal-50-50-dual-summary "]/div[@class="media-item__group"]/div[@class="media-item__image"]/div/a/picture/source/source/source/source/source/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="module"]/div[@class="media-item-list"]/section[@class="media-item orient--horizontal-33-66 "]/div[@class="media-item__image"]/div/a/@href')
        thumbnails = selector.xpath(
            '//div[@class="module"]/div[@class="media-item-list"]/section[@class="media-item orient--horizontal-33-66 "]/div[@class="media-item__image"]/div/a/picture/source/source/source/source/source/img/@data-lazy-img')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        try:
            raw.update(response.meta)
            selector = etree.HTML(response.body)
            # print(etree.tostring(selector))
            if raw['thumbnails'] == []:
                pass
            else:
                title = selector.xpath('//title/text()')[0]
                raw['title'] = title
                author = selector.xpath('//a[@rel="author"]/text()')[0]
                raw['author'] = author
                time = selector.xpath('//time/@datetime')[0].split('T')[0].split(' ')[0]
                raw['time'] = time
                raw['keywords'] = []
                raw['tags'] = ['comedy']
                raw['publisher'] = 'politico'
                raw['subtitle'] = ''
                self.parse_raw(raw)
        except:
            logging.error("this article fails to scrapy")
