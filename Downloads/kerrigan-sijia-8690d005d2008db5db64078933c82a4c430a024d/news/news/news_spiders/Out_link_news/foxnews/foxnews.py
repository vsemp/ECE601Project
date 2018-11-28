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

from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium import webdriver


class FoxnewsSpider(OutLinkNews):
    name = 'foxnews'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'foxnews'
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
        'http://foxnews.com/',
    ]

    def __init__(self, *a, **kw):
        super(FoxnewsSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)

        selector = etree.HTML(response.body)
        click_number = 2
        thumbnails = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight has-hero"]/div/article[@class="article story-1"]/div[@class="m"]/a/picture/source/source/source/source/source/img/@src')
        thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
        urls = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight has-hero"]/div/article[@class="article story-1"]/div[@class="m"]/a/@href')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        thumbnails = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-2"]/div[@class="m"]/a/picture/img/@src')
        thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
        urls = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-2"]/div[@class="m"]/a/@href')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        thumbnails = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-3"]/div[@class="m"]/a/picture/img/@src')
        thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
        urls = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-3"]/div[@class="m"]/a/@href')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        thumbnails = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-4"]/div[@class="m"]/a/picture/img/@src')
        thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
        urls = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-4"]/div[@class="m"]/a/@href')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        thumbnails = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-5"]/div[@class="m"]/a/picture/img/@src')
        thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
        urls = selector.xpath(
            '//main[@class="main-content"]/div/div/div[@class="collection collection-spotlight"]/div/article[@class="article story-5"]/div[@class="m"]/a/@href')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        for i in range(1, 17):
            thumbnails_x_path = '//div[@class="main main-secondary"]/div[@class="collection collection-article-list"]/div[@class="content article-list"]/article[@class="article story-{}"]/div[@class="m"]/a/picture/img/@data-src'.format(
                i)
            urls_x_path = '//div[@class="main main-secondary"]/div[@class="collection collection-article-list"]/div[@class="content article-list"]/article[@class="article story-{}"]/div[@class="m"]/a/@href'.format(
                i)

            thumbnails = selector.xpath(thumbnails_x_path)
            thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
            urls = selector.xpath(urls_x_path)

            for index, url in enumerate(urls):
                raw['thumbnails'] = [thumbnails[index]]
                raw['source_url'] = url
                self.content_list.append(copy.deepcopy(raw))

        thumbnails = selector.xpath(
            '//div[@class="row"]/section/div[@class="content"]/div[@class="latest"]/article[@class="article"]/div[@class="m"]/a/img/@data-src')
        thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
        urls = selector.xpath(
            '//div[@class="row"]/section/div[@class="content"]/div[@class="latest"]/article[@class="article"]/div[@class="m"]/a/@href')
        urls = ["http://" + url[2:] for url in urls]

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        # print(etree.tostring(selector))
        try:
            if raw['thumbnails'] == []:
                pass
            else:
                title = selector.xpath('//title/text()')
                raw['title'] = title[0]
                # print(title)
                raw['time'] = selector.xpath('//meta[@name="dc.date"]/@content')[0]
                # print(raw['time'])
                raw['author'] = selector.xpath('//meta[@name="dc.creator"]/@content')[0]
                # print(raw['author'])
                raw['keywords'] = []
                raw['tags'] = []
                raw['publisher'] = selector.xpath('//meta[@name="dc.publisher"]/@content')[0]
                # print(raw['publisher'])
                raw['subtitle'] = ''
            self.parse_raw(raw)

        except:
            logging.error("article fails to parse")











