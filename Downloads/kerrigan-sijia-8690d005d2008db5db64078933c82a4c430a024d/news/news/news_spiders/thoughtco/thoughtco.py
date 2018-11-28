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

class ThoughtcoSpide(NewsSpider):
    name = 'thoughtco'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'thoughtco'
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
        'https://www.thoughtco.com/astrology-4133112',
    ]

    def __init__(self, *a, **kw):
        super(ThoughtcoSpide, self).__init__(*a, **kw)
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
        # urls = selector.xpath('//a[@id="block_3-0"]/@href')
        # print(response.body)

        # thumbnails = selector.xpath('//a[@id="block_3-0"]/div[@class="block-media"]/img/@data-src')

        # print('111', len(urls), len(thumbnails))

        for elm in selector.xpath('//a[@id="block_3-0"]'):
            # print(selector.xpath('//a[@id="block_3-0"][index]/div[@class="block-media"]/img/@data-src'))
            if len(elm.getchildren()) == 2:
                raw['thumbnails'] = [elm.getchildren()[0].getchildren()[0].get('data-src')]
                raw['source_url'] = elm.get('href')
            # print(elm.get('href'))
            else:
                raw['thumbnails'] = []
                raw['source_url'] = elm.get('href')

            self.content_list.append(copy.deepcopy(raw))

        # raw['thumbnails'] = thumbnails[index]
        # self.content_list.append(copy.deepcopy(raw))

        # print('11111111'etree.HTML(response.body).xpath('//div[@class="cover-image"]/@style'))
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

    def month_transfer(self, month):
        if month == 'January':
            return '01'
        elif month == 'February':
            return '02'
        elif month == 'March':
            return '03'
        elif month == 'April':
            return '04'
        elif month == 'May':
            return '05'
        elif month == 'June':
            return '06'
        elif month == 'July':
            return '07'
        elif month == 'August':
            return '08'
        elif month == 'September':
            return '09'
        elif month == 'October':
            return '10'
        elif month == 'November':
            return '11'
        else:
            return '12'

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        content = []
        selector = etree.HTML(response.body)
        title = selector.xpath('//h1[@id="article-heading_1-0"]/text()')
        raw["title"] = title[0].strip()
        # print('1111',title)
        # print(selector.xpath('//span[@class="byline-name"]/a/text()'))
        if selector.xpath('//span[@class="byline-name"]/a/text()') != []:
            author = selector.xpath('//span[@class="byline-name"]/a/text()')
            raw["author"] = author[0]
        else:
            author = selector.xpath('//span[@class="byline-name"]/text()')
            raw["author"] = author[0]

        time = selector.xpath('//*[@id="updated-label_1-0"]/text()')
        new_time = time[0].split(',')
        new_string = new_time[1].strip()
        month_day = new_time[0].strip().split()
        if len(month_day[2]) == 2:
            new_string += '-' + self.month_transfer(month_day[1]) + '-' + month_day[2]
        else:
            new_string += '-' + self.month_transfer(month_day[1]) + '-' + '0' + month_day[2]
        raw['time'] = new_string
        raw['keywords'] = []
        raw['tags'] = ['horoscope_matrix']
        raw['publisher'] = ''
        if selector.xpath('//h2[@id="article-subheading_1-0"]/text()') != []:
            raw['subtitle'] = selector.xpath('//h2[@id="article-subheading_1-0"]/text()')[0].strip()
        else:
            raw['subtitle'] = ''
        raw['content'] = []
        dict_content = {}
        # new_html = "<html>" + "<body>" + "<h1>" + self.dict["title"][0] + "</h1>" + "<p>" + self.dict["date"][0] + "</p>" + "<img src="+self.dict["img"][0]+">"
        img = selector.xpath('//div[@class="img-placeholder"]/img/@src')
        text = ''
        rich_content = ''
        dict_content['text'] = text
        dict_content['rich_content'] = rich_content
        dict_content['image'] = img[0]
        raw['content'].append(copy.copy(dict_content))
        for elm in selector.xpath('//*[@id="flex_1-0"]/h3 |//*[@id="flex_1-0"]/p'):
            if elm.tag == 'p':
                if elm.attrib != []:
                    elm.attrib.pop('class')
                    b = etree.tostring(elm, method='html', with_tail=False)
                    b = b.encode("utf-8")
                    if 'https' in b:
                        text = re.sub('<[^>]*>', '', b)
                        rich_content = ''
                        dict_content['image'] = ''
                        dict_content['text'] = text
                        dict_content['rich_content'] = ''
                        raw['content'].append(copy.deepcopy(dict_content))
                    else:
                        dict_content['image'] = ''
                        dict_content['text'] = ''
                        dict_content['rich_content'] = b
                        raw['content'].append(copy.deepcopy(dict_content))
                else:
                    b = etree.tostring(elm, method='html', with_tail=False)
                    b = b.encode("utf-8")
                    if 'http' in b:
                        text = re.sub('<[^>]*>', '', b)
                        rich_content = ''
                        dict_content['image'] = ''
                        dict_content['text'] = text
                        dict_content['rich_content'] = ''
                        raw['content'].append(copy.deepcopy(dict_content))
                    else:
                        dict_content['image'] = ''
                        dict_content['text'] = ''
                        dict_content['rich_content'] = b
                        raw['content'].append(copy.deepcopy(dict_content))
            else:

                b = etree.tostring(elm, method='html', with_tail=False)
                b = b.encode("utf-8")
                if 'https' in b:
                    text = re.sub('<[^>]*>', '', b)
                    rich_content = ''
                    dict_content['image'] = ''
                    dict_content['text'] = text
                    dict_content['rich_content'] = ''
                    raw['content'].append(copy.deepcopy(dict_content))
                else:
                    dict_content['image'] = ''
                    dict_content['text'] = ''
                    dict_content['rich_content'] = b
                    raw['content'].append(copy.deepcopy(dict_content))

        self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(ThoughtcoSpide, self).generate_message(article_info)
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