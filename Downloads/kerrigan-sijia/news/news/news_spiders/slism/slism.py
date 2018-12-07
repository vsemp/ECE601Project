# -*- coding: utf-8 -*-
import scrapy
import copy
import re
import json
import scrapy
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



# from selenium import webdriver

class SlismSpider(NewsSpider):
    name = 'slism'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'slism'
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
        'http://slism.com/girlstalk//',
    ]

    def __init__(self, *a, **kw):
        super(SlismSpider, self).__init__(*a, **kw)
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
        urls = selector.xpath('//h3/a/@href')
        thumbnails = selector.xpath('//img[@width="80"]/@src')
        times = selector.xpath('//time/text()')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            time = times[index].split(',')
            new_string = time[1].strip().split()[0]
            month = self.month_transfer(time[0].strip().split()[0])
            date = time[0].strip().split()[1]
            if len(date) == 2:
                new_string += '-' + month + '-' + date
            else:
                new_string += '-' + month + '-' + '0' + date
            raw["time"] = new_string
            self.content_list.append(copy.deepcopy(raw))

        """
        category_id = re.findall("categoryId: \'(.*?)'", response.body)[0]
        post_body = {"category_id": category_id, "page_size": 10}
        raw['category_id'] = category_id

        r = requests.post(url="http://horoscope.ohippo.com/ajax/article/list", json=post_body)
        #print('111111', r.json())
        for each in r.json()['data']:
            raw['source_url'] = each['url']
            #raw['title'] = each['title']
            #raw['subtitle'] = ""
            raw['thumbnails'] = [each['image']]
            #raw['raw_publish_time'] = each['publish_time']
            self.content_list.append(copy.deepcopy(raw))
        last_content_id = r.json()['data'][-1]['content_id']

        while self.browse_times < self.browse_limit:
            self.browse_times += 1
            post_body = {"category_id": raw['category_id'], "page_size": 10, "last_content_id": last_content_id}
            r = requests.post(url="http://horoscope.ohippo.com/ajax/article/list", json=post_body)
            for each in r.json()['data']:
                raw['source_url'] = each['url']
                raw['title'] = each['title']
                raw['subtitle'] = ""
                raw['thumbnails'] = [each['image']]
                raw['raw_publish_time'] = each['publish_time']
                self.content_list.append(copy.deepcopy(raw))

            last_content_id = r.json()['data'][-1]['content_id']
        """

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        content = []
        selector = etree.HTML(response.body)
        title = selector.xpath("//h1/a/text()")
        raw["title"] = title[0]
        # author = selector.xpath('//p[@id="article-author"]/text()')
        raw["author"] = ''
        raw['keywords'] = []
        raw['tags'] = ['cherry_matrix']
        raw['publisher'] = ''
        raw['subtitle'] = ''
        raw['content'] = []
        dict_content = {}
        for elm in selector.xpath('//*[@id="slism-main-article"]/child::*'):
            if 'class' in elm.attrib:
                elm.attrib.pop('class')
            if elm.tag != 'div' and elm.tag != 'aside':
                if elm.tag == 'img':
                    image = elm.get('src')
                    text = ''
                    rich_content = ''
                    dict_content['text'] = text
                    dict_content['image'] = image
                    dict_content['rich_content'] = rich_content
                    raw['content'].append(copy.deepcopy(dict_content))
                else:
                    b = etree.tostring(elm, method='html', with_tail=False)
                    b = b.decode("utf-8")
                    if 'http' in b:
                        text = re.sub('<[^>]*>', '', b)
                        rich_content = ''
                        dict_content['image'] = ''
                        dict_content['text'] = text
                        dict_content['rich_content'] = ''
                        raw['content'].append(copy.deepcopy(dict_content))
                    else:
                        b = b.decode("utf-8")
                        dict_content['image'] = ''
                        dict_content['text'] = ''
                        dict_content['rich_content'] = b
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
        message = super(SlismSpider, self).generate_message(article_info)
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
