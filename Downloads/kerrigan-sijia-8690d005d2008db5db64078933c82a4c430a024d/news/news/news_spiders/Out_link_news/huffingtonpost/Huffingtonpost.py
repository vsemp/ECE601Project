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


class HuffingtonpostSpider(OutLinkNews):
    name = 'huffingtonpost'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'huffingtonpost'
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
        'http://huffingtonpost.com/',
    ]

    def __init__(self, *a, **kw):
        super(HuffingtonpostSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)

        selector = etree.HTML(response.body)
        click_number = 2
        # print(etree.tostring(selector))
        urls = selector.xpath(
            '//section/div[@class="zone__content"]/div[@class="card card--media-left card--standard card--twilight js-card yr-card"]/div/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//section/div[@class="zone__content"]/div[@class="card card--media-left card--standard card--twilight js-card yr-card"]/div/a/div[@class="card__image js-card-image"]/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//section[@class="js-zone-friend yr-zone zone zone--friend zone--shaft"]/div[@class="zone__content"]/div/div/div/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//section[@class="js-zone-friend yr-zone zone zone--friend zone--shaft"]/div[@class="zone__content"]/div/div/div/a/div/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//section[@class="js-zone-danger yr-zone zone zone--danger zone--shaft"]/div[@class="zone__content"]/div[@class="card card--danger card--media-top card--standard js-card yr-card"]/div/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//section[@class="js-zone-danger yr-zone zone zone--danger zone--shaft"]/div[@class="zone__content"]/div[@class="card card--danger card--media-top card--standard js-card yr-card"]/div/a/div/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//section[@class="js-zone-left yr-zone zone zone--left"]/div[@class="zone__content"]/div/div/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//section[@class="js-zone-left yr-zone zone zone--left"]/div[@class="zone__content"]/div/div/a/div/img/@src')
        thumbnails = [thumbnails[0]] + thumbnails[2:]
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//section[@class="js-zone-center yr-zone zone zone--center zone--shaft"]/div[@class="zone__content"]/div/div/div/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//section[@class="js-zone-center yr-zone zone zone--center zone--shaft"]/div[@class="zone__content"]/div/div/div/a/div/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        #print(etree.tostring(selector))
        if raw['thumbnails'] == []:
            pass
        else:
            try:
                title = selector.xpath('//h1[@class="headline__title"]/text()')[0]
                raw['title'] = title
                raw['time'] = selector.xpath('//meta[@property="article:published_time"]/@content')[0].split(' ')[0]
                raw['author'] = selector.xpath('//a[@class="author-card__link yr-author-name"]/text()')[0]
                raw['keywords'] = []
                raw['tags'] = []
                raw['publisher'] = 'huffpost'
                raw['subtitle'] = selector.xpath('//div[@class="headline__subtitle"]/text()')[0]

                self.parse_raw(raw)
            except:
                logging.error("article fails to parse")



