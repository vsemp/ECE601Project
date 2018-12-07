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
import hashlib
import datetime
from ....spider_const import *
from ..out_link_news import OutLinkNews

from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium import webdriver


class BbcSpider(OutLinkNews):
    name = 'bbc'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'bbc'
    input_type = INPUT_TYPE_CRAWL
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
        'http://bbc.com/',
    ]

    def __init__(self, *a, **kw):
        super(BbcSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop(0)
            # source_url 去重
            if self.is_source_url_exist(self.input_type, raw['source_url']):
                self.logger.info('source_url exists: ' + str(raw['source_url']))
                self.spider_idle()
            else:
                self.logger.warning('content_list pop ed')
                rq = Request(
                    raw['source_url'],
                    headers=self.hd,
                    meta=raw,
                    dont_filter=True,
                    callback=self.parse_page
                )
                self.crawler.engine.crawl(rq, self)
        elif self.channel_list:
            self.browse_times = 0
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
        # click_number = 2
        # print(etree.tostring(selector))
        try:
            thumbnails = \
                selector.xpath('//li[@class="media-list__item media-list__item--1"]/div/div/div/div/@data-src')[0]

            urls = selector.xpath(
                '//li[@class="media-list__item media-list__item--1"]/div/div[@class="media__content"]/h3/a/@href')[0]
            urls = response.urljoin(urls)
            raw['thumbnails'] = [thumbnails.replace('{width}', '750')]
            raw['source_url'] = urls
            self.content_list.append(copy.deepcopy(raw))

            for i in range(2, 6):
                thumbnails_link = '//li[@class="media-list__item media-list__item--{}"]/div/div/div/div/@data-src'.format(
                    i)
                urls_link = '//li[@class="media-list__item media-list__item--{}"]/div/div[@class="media__content"]/h3/a/@href'.format(
                    i)
                thumbnails = selector.xpath(thumbnails_link)[0]
                urls = selector.xpath(urls_link)[0]
                urls = response.urljoin(urls)

                raw['thumbnails'] = [thumbnails.replace('{width}', '750')]
                raw['source_url'] = urls
                self.content_list.append(copy.deepcopy(raw))

            thumbnails = selector.xpath(
                '//section[@class="module module--collapse-images module--collapse-images module--highlight module--editors-picks"]/div/div/div/ul/li/div/div/div//div/@data-src')
            urls = selector.xpath(
                '//section[@class="module module--collapse-images module--collapse-images module--highlight module--editors-picks"]/div/div/div/ul/li/div/div[@class="media__content"]/h3/a/@href')
            urls = [response.urljoin(url) for url in urls]

            for index, url in enumerate(urls):
                raw['thumbnails'] = [thumbnails[index].replace('{width}', '750')]
                raw['source_url'] = url
                self.content_list.append(copy.deepcopy(raw))

            thumbnails = selector.xpath(
                '//section[@class="module module--collapse-images module--special-features module--primary-special-features"]/div/ul/li/div/div/div/div/div/div/@data-src')

            urls = selector.xpath(
                '//section[@class="module module--collapse-images module--special-features module--primary-special-features"]/div/ul/li/div/div/div/div[@class="media__content"]/h3/a/@href')
            urls = [response.urljoin(url) for url in urls]
            for index, url in enumerate(urls):
                raw['thumbnails'] = [thumbnails[index].replace('{width}', '750')]
                raw['source_url'] = url
                self.content_list.append(copy.deepcopy(raw))

            urls = selector.xpath(
                '//section[@class="module module--collapse-images module--highlight module--more-bbc"]/div/div/div/ul/li/div/div[@class="media__content"]/h3/a/@href')
            urls = [response.urljoin(url) for url in urls]
            thumbnails = selector.xpath(
                '//section[@class="module module--collapse-images module--highlight module--more-bbc"]/div/div/div/ul/li/div/div/div/div/@data-src')
            for index, url in enumerate(urls):
                raw['thumbnails'] = [thumbnails[index].replace('{width}', '750')]
                raw['source_url'] = url
                self.content_list.append(copy.deepcopy(raw))
        except:
            logging.error("The article fails to parse")

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        if raw['thumbnails'] == []:
            pass
        else:
            try:
                if selector.xpath('//div[@class="story-body__inner"]/child::*'):
                    title = selector.xpath('//title/text()')
                    raw['title'] = title[0]
                    time = selector.xpath('//li[@class="mini-info-list__item"]/div[@class="date date--v2"]/text()')[
                        0].split()
                    new_string = time[2]
                    month = self.month_transfer(time[1])
                    date = time[0]
                    if len(date) == 2:
                        new_string += '-' + month + '-' + date
                    else:
                        new_string += '-' + month + '-' + '0' + date
                    raw['time'] = new_string
                    raw['author'] = ''
                    # print(raw['author'])
                    raw['keywords'] = []
                    raw['tags'] = []
                    raw['publisher'] = 'bbc'
                    raw['subtitle'] = ''
                    raw['content'] = []
                    dict_content = {}
                    count = 0
                    count_1 = 0

                    for elm in selector.xpath('//div[@class="story-body__inner"]/child::*'):
                        if elm.tag == 'p':
                            content = etree.tostring(elm, method='html', with_tail=False)
                            content = content.encode("utf-8")

                            text = re.sub('<[^>]*>', '', content)

                            if text != '' and text != '.' and text != '&#160;' and "sign up for the weekly bbc.com" not in text and \
                                            "To comment on this story or anything else you have seen on BBC Capital" not in text and text != "&#160;--" \
                                    and "If you would like to comment on this story" not in text:
                                rich_content = ''
                                dict_content['image'] = ''
                                dict_content['text'] = text
                                dict_content['rich_content'] = ''
                                raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'ul':
                            for sub_elm in elm.getchildren():
                                content = etree.tostring(sub_elm, method='html', with_tail=False)
                                content = content.encode("utf-8")
                                text = re.sub('<[^>]*>', '', content)
                                if text != '':
                                    rich_content = ''
                                    dict_content['image'] = ''
                                    dict_content['text'] = text
                                    dict_content['rich_content'] = ''
                                    raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'h2':
                            try:
                                del elm.attrib["class"]
                            except KeyError:
                                pass
                            content = etree.tostring(elm, method='html', with_tail=False)
                            content = content.encode("utf-8")
                            rich_content = content
                            dict_content['image'] = ''
                            dict_content['text'] = ''
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))

                        elif elm.tag == 'figure' and (elm.attrib['class'] == "media-landscape has-caption full-width" or
                                                              elm.attrib[
                                                                  'class'] == "media-landscape no-caption full-width"
                                                      or elm.attrib[
                                'class'] == "media-portrait no-caption full-width" or elm.attrib[
                            'class'] == "media-landscape no-caption full-width lead" or
                                                              elm.attrib[
                                                                  'class'] == "media-landscape has-caption full-width lead"):
                            if elm.attrib['class'] != "media-landscape has-caption full-width lead" and elm.attrib[
                                'class'] != "media-landscape no-caption full-width lead":

                                img = elm.xpath('//figure[contains(@class,"full-width")]/span/div/@data-src')[count]
                                count += 1
                            else:
                                img = elm.xpath('//figure[contains(@class,"full-width")]/span/img/@src')[count_1]
                                count_1 += 1
                            dict_content['image'] = img
                            dict_content['text'] = ''
                            dict_content['rich_content'] = ''
                            raw['content'].append(copy.deepcopy(dict_content))


                else:
                    title = selector.xpath('//title/text()')
                    raw['title'] = title[0]

                    time = selector.xpath('//span[@class="publication-date index-body"]/text()')[0].split()
                    new_string = time[2]
                    month = self.month_transfer(time[1])
                    date = time[0]
                    if len(date) == 2:
                        new_string += '-' + month + '-' + date
                    else:
                        new_string += '-' + month + '-' + '0' + date
                    raw['time'] = new_string

                    raw['author'] = selector.xpath('//meta[@name="author"]/@content')[0]

                    raw['keywords'] = []
                    raw['tags'] = []
                    raw['publisher'] = 'bbc'
                    raw['subtitle'] = ''
                    raw['content'] = []
                    dict_content = {}
                    count = 0
                    count_1 = 0
                    for elm in selector.xpath('//div[@class="body-content"]/child::*'):
                        if elm.tag == 'p':
                            content = etree.tostring(elm, method='html', with_tail=False)
                            content = content.encode("utf-8")

                            text = re.sub('<[^>]*>', '', content)
                            if text != '' and text != '.' and text != '&#160;' and "sign up for the weekly bbc.com" not in text and \
                                            "To comment on this story or anything else you have seen on BBC Capital" not in text and text != "&#160;--" \
                                    and "If you would like to comment on this story" not in text:
                                rich_content = ''
                                dict_content['image'] = ''
                                dict_content['text'] = text
                                dict_content['rich_content'] = ''
                                raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'ul':
                            for sub_elm in elm.getchildren():
                                content = etree.tostring(sub_elm, method='html', with_tail=False)
                                content = content.encode("utf-8")
                                text = re.sub('<[^>]*>', '', content)
                                if text != '':
                                    rich_content = ''
                                    dict_content['image'] = ''
                                    dict_content['text'] = text
                                    dict_content['rich_content'] = ''
                                    raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'h2':
                            try:
                                del elm.attrib["class"]
                            except KeyError:
                                pass
                            content = etree.tostring(elm, method='html', with_tail=False)
                            content = content.encode("utf-8")
                            rich_content = content
                            dict_content['image'] = ''
                            dict_content['text'] = ''
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))

                        elif elm.tag == 'figure' and (
                                                elm.attrib['class'] == "media-landscape has-caption full-width" or
                                                elm.attrib[
                                                    'class'] == "media-landscape no-caption full-width"
                                    or elm.attrib['class'] == "media-portrait no-caption full-width" or elm.attrib[
                                    'class'] == "media-landscape no-caption full-width lead"):
                            if elm.xpath('//figure[contains(@class,"full-width")]/span/div/@data-src') != []:
                                img = elm.xpath('//figure[contains(@class,"full-width")]/span/div/@data-src')[count]
                                count += 1
                            else:
                                img = elm.xpath('//figure[contains(@class,"full-width")]/span/img/@src')[count_1]
                                count_1 += 1

                                dict_content['image'] = img
                                dict_content['text'] = ''
                                dict_content['rich_content'] = ''
                                raw['content'].append(copy.deepcopy(dict_content))

                self.parse_raw(raw)


            except:
                logging.error("article fails to parse")

    def month_transfer(self, month):
        if month == 'Jan.':
            return '01'
        elif month == 'Feb.':
            return '02'
        elif month == 'Mar.':
            return '03'
        elif month == 'Apr.':
            return '04'
        elif month == 'May':
            return '05'
        elif month == 'June':
            return '06'
        elif month == 'July':
            return '07'
        elif month == 'Aug.':
            return '08'
        elif month == 'Sept':
            return '09'
        elif month == 'Oct.':
            return '10'
        elif month == 'Nov.':
            return '11'
        else:
            return '12'

    def get_extra_from_raw(self, raw):
        return {'news_type': 'external_link'}
