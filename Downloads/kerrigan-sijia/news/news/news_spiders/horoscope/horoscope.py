# -*- coding: utf-8 -*-
import scrapy
import copy
import re
import scrapy
import json
from scrapy import signals
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
import requests
import lxml
# from feeds_back_utils import *
from lxml import etree
import traceback
import pprint
import hashlib
import datetime
from ..news_spider_base import NewsSpider
from ...spider_const import *
import json
import httplib
from selenium import webdriver
import os

class HoroscopeSpider(NewsSpider):
    name = 'horoscope'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'horoscope'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': '',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 1
    page_times = 0
    page_limit = 1
    content_list = []
    channel_list = [
        'https://www.horoscope.com/articles',

    ]

    def __init__(self, *a, **kw):
        super(HoroscopeSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop(0)
            # source_url 去重
            # if raw['inlinks'][0] == 'https://www.horoscope.com/articles':

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
        print('555')
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

    def parse_list(self, response):
        try:
            raw = dict()
            raw.update(response.meta)
            parent_path = os.path.abspath(os.path.join(os.path.dirname('phantomjs-2.1.1-linux'), os.path.pardir))
            parent_path += '/news/news/news_spiders/phantomjs-2.1.1-linux/bin/phantomjs'
            driver = webdriver.PhantomJS(executable_path=parent_path)
            driver.get(response.url)
            selector = etree.HTML(driver.page_source)
            urls = selector.xpath('//li[@class="row mtop-1"]/a/@href')
            thumbnails = selector.xpath('//li[@class="row mtop-1"]/a/img/@data-original')
            for index, url in enumerate(urls):
                raw['source_url'] = url
                raw['thumbnails'] = [thumbnails[index]]
                self.content_list.append(copy.deepcopy(raw))
            next_links = selector.xpath('//h3[@class="pagination"]/a/@href')
            next_links = [response.urljoin(next_link) for next_link in next_links]
            for next_link in next_links:
                self.channel_list.append(next_link)

        except httplib.BadStatusLine:
            pass

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        content = []
        parent_path = os.path.abspath(os.path.join(os.path.dirname('phantomjs-2.1.1-linux'), os.path.pardir))
        parent_path += '/news/news/news_spiders/phantomjs-2.1.1-linux/bin/phantomjs'
        driver = webdriver.PhantomJS(executable_path=parent_path)
        driver.get(response.url)
        selector = etree.HTML(driver.page_source)
        title = selector.xpath('//h1[@class="title"]/text()')
        raw["title"] = title[0]
        time = selector.xpath('//li/h5/span/text()')[0].split(',')
        new_string = time[1].strip().split()[0]
        month = self.month_transfer(time[0].strip().split()[0])
        date = time[0].strip().split()[1]
        if len(date) == 2:
            new_string += '-' + month + '-' + date
        else:
            new_string += '-' + month + '-' + '0' + date
        raw["time"] = new_string
        publisher = selector.xpath('//li/h5/a/text()')
        raw['publisher'] = publisher[1]
        raw['author'] = publisher[0]
        raw['keywords'] = []
        raw['tags'] = ['horoscope_matrix']
        raw['subtitle'] = ''
        raw['content'] = []
        dict_content = {}
        if selector.xpath('//img[@class="img-responsive mtop-2"]/@data-original'):
            image = selector.xpath('//img[@class="img-responsive mtop-2"]/@data-original')
        else:
            image = selector.xpath('//img[@class="img-responsive mtop-2"]/@src')
        rich_content = ''
        dict_content['image'] = image[0]
        dict_content['text'] = ''
        dict_content['rich_content'] = ''
        raw['content'].append(copy.deepcopy(dict_content))
        for elm in selector.xpath('//div[@class="span-12 span-sm-12 span-xs-12 col"]/child::*'):
            if elm.tag == 'p':

                if elm.getchildren() != [] and elm.getchildren()[0].getchildren() != [] and elm.getchildren()[
                    0].tag == 'a' and elm.getchildren()[0].getchildren()[0].tag == 'i':
                    continue
                if elm.getchildren() != [] and elm.getchildren()[0].getchildren() != [] and elm.getchildren()[
                    0].tag == 'a' and elm.getchildren()[0].getchildren()[0].tag == 'em':
                    continue
                if elm.getchildren() != [] and elm.getchildren()[0].getchildren() != [] and elm.getchildren()[
                    0].tag == 'em' and elm.getchildren()[0].getchildren()[0].tag == 'a':
                    continue
                if 'Read this now' in etree.tostring(elm, method='html',
                                                     with_tail=False) and elm.getchildren() != [] and (
                    elm.getchildren()[0].tag or elm.getchildren()[1].tag) == 'a':
                    continue

                if 'Read This Now' in etree.tostring(elm, method='html',
                                                     with_tail=False) and elm.getchildren() != [] and elm.getchildren()[
                    1].tag == 'a':
                    continue
                b = etree.tostring(elm, method='html', with_tail=False)
                if b[3:-4] != '&#160;':
                    if 'http' in b:

                        text = re.sub('<[^>]*>', '', b)
                        rich_content = ''
                        dict_content['image'] = ''
                        dict_content['text'] = text
                        dict_content['rich_content'] = ''
                        raw['content'].append(copy.deepcopy(dict_content))
                    else:

                        text = re.sub('<[^>]*>', '', b)
                        if "Read the latest" in text:
                            break
                        rich_content = b.decode("utf-8")
                        dict_content['image'] = ''
                        dict_content['text'] = ''
                        dict_content['rich_content'] = rich_content
                        raw['content'].append(copy.deepcopy(dict_content))
            if elm.tag == 'h2':
                if 'http' in b:

                    text = re.sub('<[^>]*>', '', b)
                    rich_content = ''
                    dict_content['image'] = ''
                    dict_content['text'] = text
                    dict_content['rich_content'] = ''
                    raw['content'].append(copy.deepcopy(dict_content))
                else:

                    text = re.sub('<[^>]*>', '', b)
                    if "Read the latest" in text:
                        break
                    rich_content = b.decode("utf-8")
                    dict_content['image'] = ''
                    dict_content['text'] = ''
                    dict_content['rich_content'] = rich_content
                    raw['content'].append(copy.deepcopy(dict_content))
            if elm.tag == 'ol':
                b = etree.tostring(elm, method='html', with_tail=False)
                rich_content = b.decode("utf-8")
                dict_content['image'] = ''
                dict_content['text'] = ''
                dict_content['rich_content'] = rich_content
                raw['content'].append(copy.deepcopy(dict_content))
            if elm.tag == 'div' and elm.attrib == []:
                return {}
        self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(HoroscopeSpider, self).generate_message(article_info)
        if 'inlinks' in article_info['raw']:
            message['inlinks'] = article_info['raw']['inlinks']
        return message

    def get_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_html_from_raw(self, raw):
        return ''

    def get_raw_tags_from_raw(self, raw):
        tag_list = raw['tags']
        return tag_list

    def get_title_from_raw(self, raw):
        return raw['title']

    def get_thumbnails_from_raw(self, raw):
        return raw['thumbnails']

    def get_doc_id_from_raw(self, raw):
        return hashlib.md5(str(raw['source_url'])).hexdigest()

    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    def get_locale_from_raw(self, raw):
        return self.locale

    def get_content_from_raw(self, raw):
        return raw['content']

    def get_publish_time_from_raw(self, raw):
        return str(datetime.datetime.now())[:19]

    def get_keywords_from_raw(self, raw):
        return []

    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_extra_from_raw(self, raw):
        return {'key': 'extra_key'}

    def get_publisher_from_raw(self, raw):
        return ""

    def get_publisher_icon_from_raw(self, raw):
        return []

    def get_publisher_id_from_raw(self, raw):
        return -1

    def get_source_name_from_raw(self, raw):
        return self.source_name

    def get_subtitle_from_raw(self, raw):
        return raw['subtitle']

    def get_input_type_from_raw(self, raw):
        return self.input_type
