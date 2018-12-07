# -*- coding: utf-8 -*-
import copy
import re
import scrapy
from scrapy import signals
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
import requests
import lxml
import json
# from feeds_back_utils import *
from lxml import etree
import traceback
import pprint
import datetime
import hashlib
from ..news_spider_base import NewsSpider
from ...spider_const import *


class YourtangoSpider(NewsSpider):
    name = 'yourtango'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'yourtango'
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
        'https://www.yourtango.com/zodiac/',

    ]
    page_next = []
    count = 0
    limit = 2
    page_count = 0
    count_1 = 0

    def __init__(self, *a, **kw):
        super(YourtangoSpider, self).__init__(*a, **kw)
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
        else:
            if self.count <= self.limit:
                if len(self.page_next) != 0:
                    web_address = self.page_next.pop()
                    self.logger.warning('page_next pop ed')
                    dict_url = {}
                    dict_url['inlinks'] = web_address
                    rq = Request(
                        url=web_address,
                        meta=dict_url,
                        headers=self.hd,
                        dont_filter=True,
                        callback=self.parse_list
                    )
                    self.crawler.engine.crawl(rq, self)


                # self.browse_times = 0
                # for rq in self.start_requests():
                #    self.crawler.engine.crawl(rq, self)

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
        urls = selector.xpath('//div[@class="teaser-mix-left"]/h2/a/@href')
        urls = [response.urljoin(url) for url in urls]
        # print(response.body)
        thumbnails = selector.xpath('//div[@class="image-bx col-lg-6 col-md-6 col-sm-6"]/a/img/@src')
        next_links = selector.xpath('//li[@class="next"]/a/@href')
        if self.count_1 < 2:
            next_links = [response.urljoin(next_link) for next_link in next_links]
            self.page_next.append(next_links[0])
            self.count_1 += 1
            print(self.page_next)
        for i in range(len(urls)):
            raw['source_url'] = urls[i]
            raw['thumbnails'] = [thumbnails[i]]
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        content = []
        self.page_count += 1
        print(self.page_count)
        dict_content = {}
        selector = etree.HTML(response.body)
        raw['title'] = selector.xpath('//h1[@class="page-header"]/text()')[0]
        author = selector.xpath('//div[@class="author-name"]/div/a[@data-type="profile"]/span/text()')
        raw['author'] = author[0]
        raw['keywords'] = []
        raw['tags'] = []
        raw['publisher'] = ''
        raw['subtitle'] = ''
        time = selector.xpath('//div[@class="post-date"]/text()')
        new_time = time[0].split(',')
        new_string = new_time[1]
        month_day = new_time[0].strip().split()
        if len(month_day[1]) == 2:
            new_string += '-' + self.month_transfer(month_day[0]) + '-' + month_day[1]
        else:
            new_string += '-' + self.month_transfer(month_day[0]) + '-' + '0' + month_day[1]
        raw['time'] = new_string
        img = selector.xpath('//div[@class="image field-item even"]/img/@src')
        image = img[0]
        text = ''
        rich_content = ''
        dict_content['image'] = image
        dict_content['rich_content'] = rich_content
        dict_content['text'] = text
        raw['content'] = []
        raw['content'].append(copy.deepcopy(dict_content))
        for elm in selector.xpath('//div[@class="yt-node-content"]/p | //div[@class="yt-node-content"]/h2'):
            b = etree.tostring(elm, method='html', with_tail=False)
            b = b.decode("utf-8")
            image = ''
            text = ''
            rich_content = b
            dict_content['image'] = image
            dict_content['rich_content'] = rich_content
            dict_content['text'] = text
            raw['content'].append(copy.deepcopy(dict_content))

        self.parse_raw(raw)


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

    def generate_message(self, article_info):
        message = super(YourtangoSpider, self).generate_message(article_info)
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
        return []

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
