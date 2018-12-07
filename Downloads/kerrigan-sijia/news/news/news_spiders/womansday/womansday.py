# -*- coding: utf-8 -*-
import scrapy
import copy
import re
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
import time
import pprint
import hashlib
import datetime
from ..news_spider_base import NewsSpider
from ...spider_const import *
import json

from selenium import webdriver
import os
# # encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

# from x_path import *
# from ..fetcher import Fetcher
# from selenium import webdriver

class WomansdaySpider(NewsSpider):
    name = 'womansday'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'womansday'
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
        'https://www.womansday.com/',
    ]

    def __init__(self, *a, **kw):
        super(WomansdaySpider, self).__init__(*a, **kw)
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
        parent_path = os.path.abspath(os.path.join(os.path.dirname('phantomjs-2.1.1-linux'), os.path.pardir))
        parent_path += '/news/news/news_spiders/phantomjs-2.1.1-linux/bin/phantomjs'
        driver = webdriver.PhantomJS(executable_path=parent_path)

        driver.get(response.url)
        selector = etree.HTML(driver.page_source)

        for i in range(1, 10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        selector = etree.HTML(driver.page_source)
        # print(driver.page_source)
        urls = selector.xpath('//div[@class="full-item "]/a[@class="full-item-image item-image"]/@href')
        results = []
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath('//div[@class="full-item "]/a[@class="full-item-image item-image"]/img/@data-src')

        for index, url in enumerate(urls):
            #print('11111', url, thumbnails[index])
            raw['source_url'] = url
            raw['thumbnails'] = [thumbnails[index]]
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

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        content = []
        parent_path = os.path.abspath(os.path.join(os.path.dirname('phantomjs-2.1.1-linux'), os.path.pardir))
        parent_path += '/news/news/news_spiders/phantomjs-2.1.1-linux/bin/phantomjs'
        driver = webdriver.PhantomJS(executable_path=parent_path)
        driver.get(response.url)
        selector = etree.HTML(driver.page_source)
        if selector.xpath('//div[@class="article-body-content standard-body-content"]/child::*') != []:
            title = selector.xpath('//h1/text()')
            raw["title"] = title[0]
            time = selector.xpath('//time[@class="content-info-date js-date"]/text()')[0].split(',')
            new_string = time[1].strip()
            month = self.month_transfer(time[0].strip().split()[0])
            date = time[0].strip().split()[1]
            if len(date) == 2:
                new_string += '-' + month + '-' + date
            else:
                new_string += '-' + month + '-' + '0' + date
            raw["time"] = new_string
            author = selector.xpath('//a[@class="byline-name"]/text()')
            if author == []:
                author = selector.xpath('//span[@class="byline-name"]/text()')
            raw['author'] = author[0]
            # print('333', author)
            # print(etree.tostring(selector))
            subtitle = selector.xpath('//div[@class="content-header-inner"]/p/text()')
            # print('010',subtitle)
            raw['subtitle'] = subtitle[0]
            raw['keywords'] = []
            raw['tags'] = ['cherry_matrix']
            raw['publisher'] = ''
            raw['content'] = []
            dict_content = {}
            image = selector.xpath('//div[@class="content-lede-image-wrap"]/img/@src')
            text = ''
            rich_content = ''
            dict_content["image"] = image[0]
            dict_content["rich_content"] = rich_content
            dict_content["text"] = text
            raw['content'].append(copy.deepcopy(dict_content))
            for elm in selector.xpath('//div[@class="article-body-content standard-body-content"]/child::*'):
                if elm.tag == 'p':
                    if elm.attrib != None:
                        elm.attrib.pop('class')
                    b = etree.tostring(elm, method='html', with_tail=False)
                    text = re.sub('<[^>]*>', '', b)
                    if text == '':
                        continue
                    if 'National Suicide Prevention Lifeline' in text:
                        continue
                    if "BUY NOW" in text:
                        continue
                    rich_content = ''
                    image = ''
                    dict_content["image"] = image
                    dict_content["rich_content"] = rich_content
                    dict_content["text"] = text
                    raw['content'].append(copy.deepcopy(dict_content))
                if elm.tag == 'ul':
                    elm.attrib.pop('class')
                    b = etree.tostring(elm, method='html', with_tail=False)
                    rich_content = b
                    image = ''
                    text = ''
                    dict_content["image"] = image
                    dict_content["rich_content"] = rich_content
                    dict_content["text"] = text
                    raw['content'].append(copy.deepcopy(dict_content))
                if elm.tag == 'h2':
                    elm.attrib.pop('class')
                    b = etree.tostring(elm, method='html', with_tail=False)
                    rich_content = b
                    image = ''
                    text = ''
                    dict_content["image"] = image
                    dict_content["rich_content"] = rich_content
                    dict_content["text"] = text
                    raw['content'].append(copy.deepcopy(dict_content))
                if elm.tag == 'h3':
                    elm.attrib.pop('class')
                    b = etree.tostring(elm, method='html', with_tail=False)
                    rich_content = b
                    image = ''
                    text = ''
                    dict_content["image"] = image
                    dict_content["rich_content"] = rich_content
                    dict_content["text"] = text
                    raw['content'].append(copy.deepcopy(dict_content))

                if elm.tag == 'div' and elm.get('class') == 'embed embed-image embed-image-center embed-image-medium':
                    image = elm.xpath('//source/img/@data-srcset')
                    # print('0909', image)
                    text = ''
                    rich_content = ''
                    dict_content["image"] = image[0]
                    dict_content["rich_content"] = rich_content
                    dict_content["text"] = text
                    raw['content'].append(copy.deepcopy(dict_content))
            self.logger.warning(raw)
            self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(WomansdaySpider, self).generate_message(article_info)
        if 'inlinks' in article_info['raw']:
            message['inlinks'] = article_info['raw']['inlinks']
        return message

    def month_transfer(self, month):
        if month == 'Jan.' or month == 'Jan':
            return '01'
        elif month == 'Feb.' or month == 'Feb':
            return '02'
        elif month == 'Mar.' or month == 'Mar':
            return '03'
        elif month == 'Apr.' or month == 'Apr':
            return '04'
        elif month == 'May':
            return '05'
        elif month == 'Jun' or month == 'June':
            return '06'
        elif month == 'July' or month == 'Jul':
            return '07'
        elif month == 'Aug.' or month == 'Aug':
            return '08'
        elif month == 'Sept':
            return '09'
        elif month == 'Oct.' or month == 'Oct':
            return '10'
        elif month == 'Nov.' or month == 'Nov':
            return '11'
        elif month == 'Dec.' or month == 'Dec':
            return '12'
        else:
            self.logger.warning("Month Transfer Problem")

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

