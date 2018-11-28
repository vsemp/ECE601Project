# -*- coding: utf-8 -*-
import scrapy
import copy
import re
import json
import copy
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
import json

from selenium import webdriver
import os

class GlamourSpider(NewsSpider):
    name = 'glamour'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'glamour'
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
        'https://www.glamour.com/entertainment',
        'https://www.glamour.com/fashion',
    ]

    def __init__(self, *a, **kw):
        super(GlamourSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop(0)
            # source_url 去重
            if raw['inlinks'][0] == 'https://www.glamour.com/entertainment':

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
            else:

                if False:
                    self.logger.info('source_url exists: ' + str(raw['source_url']))
                    self.spider_idle()
                else:
                    self.logger.warning('content_list pop ed')
                    rq = Request(
                        raw['source_url'],
                        headers=self.hd,
                        meta=raw,
                        dont_filter=True,
                        callback=self.parse_page_1
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
        # urls = selector.xpath('//div[@class="feature-item-content"]/a[@class="feature-item-link feature-item-link-hed"]/@href')
        # print(etree.tostring(selector))
        if raw['inlinks'][0] == 'https://www.glamour.com/entertainment':

            urls = selector.xpath('//a[@class="feature-item-link"]/@href')
            urls = [response.urljoin(url) for url in urls if '/story/' in url]
            for url in urls:
                raw['thumbnails'] = []
                raw['source_url'] = url
                self.content_list.append(copy.deepcopy(raw))
        else:

            urls = selector.xpath('//a[@class="feature-item-link"]/@href')
            urls = [response.urljoin(url) for url in urls if '/story/' in url]
            for url in urls:
                raw['thumbnails'] = []
                raw['source_url'] = url
                self.content_list.append(copy.deepcopy(raw))
        # print(urls)
        # thumbnails = selector.xpath('//a[@class="feature-item-link"]/img/@src')
        # thumbnials = [response.urljoin(thumbnail) for thumbnail in thumbnails]
        # print('1111', len(urls),len(thumbnails))

        # print('111', len(urls), len(thumbnails))
        """
        for elm in selector.xpath('//a[@id="block_3-0"]'):
        	#print(selector.xpath('//a[@id="block_3-0"][index]/div[@class="block-media"]/img/@data-src'))
        	if len(elm.getchildren()) == 2:
        		raw['thumbnails'] = elm.getchildren()[0].getchildren()[0].get('data-src')
        		raw['source_url'] = elm.get('href')
        		#print(elm.get('href'))
        	else:
        		raw['thumbnails'] = ''
        		raw['source_url'] = elm.get('href')
        """
        # self.content_list.append(copy.deepcopy(raw))

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
        count = 1
        raw = dict()
        raw.update(response.meta)
        content = []
        selector = etree.HTML(response.body)
        if 'out for yourself' in response.body:
            pass
        else:
            title = selector.xpath('//h1/text()')
            raw["title"] = title[0]
            dict_content = {}

            raw["author"] = selector.xpath('//div[@class="contributor"]/a[@class="contributor__link"]/text()')[0]
            # print(selector.xpath('//time[class="byline__pubdate"]/text()'))
            time = selector.xpath('//time[@class="byline__pubdate"]/text()')[0].split(',')

            new_string = time[1].strip().split()[0]
            month = self.month_transfer(time[0].strip().split()[0])
            date = time[0].strip().split()[1]
            if len(date) == 2:
                new_string += '-' + month + '-' + date
            else:
                new_string += '-' + month + '-' + '0' + date

            raw["time"] = new_string
            raw['keywords'] = []
            raw['tags'] = ['cherry_matrix']
            raw['publisher'] = ''
            raw['subtitle'] = ''
            raw['content'] = []
            # date = selector.xpath('/html/body/div[1]/section/article/p[@class="create_time"]/text()')
            # self.dict["date"] = date
            # mage = selector.xpath('//div[@class="image-content"]/picture/img/@src')
            image = selector.xpath('//div[@class="image-content"]/picture/source/source/img/@src')
            if image == []:
                image = selector.xpath('//div[@class="image-content"]/picture/img/@src')

            raw["thumbnails"] = [image[0]]

            text = ''
            rich_content = ''
            dict_content['text'] = text
            dict_content['image'] = image[0]
            dict_content['rich_content'] = rich_content
            raw['content'].append(copy.deepcopy(dict_content))
            # new_html = "<html>" + "<body>" + "<h1>" + self.dict["title"][0] + "</h1>" +"<p>" + self.dict["date"][0]+ "</p>"
            for elm in selector.xpath('//div[@class="article__content"]/child::*'):
                if elm.tag == 'p':
                    if elm.attrib != []:
                        b = etree.tostring(elm, method='html', with_tail=False)
                        b = b.decode("utf-8")
                        if "Related Stories:" in b:
                            break
                        text = re.sub('<[^>]*>', '', b)
                        rich_content = ''
                        dict_content['image'] = ''
                        dict_content['text'] = text
                        dict_content['rich_content'] = ''
                        raw['content'].append(copy.deepcopy(dict_content))
                if elm.tag == 'figure':
                    img = elm.xpath('//picture/img/@src')[count]
                    dict_content['image'] = img
                    dict_content['text'] = ''
                    dict_content['rich_content'] = ''
                    raw['content'].append(copy.deepcopy(dict_content))
                    count += 1

            # self.parse_raw(raw)
            with open('data1.txt', 'a') as fh:
                json.dump(raw, fh)

    def parse_page_1(self, response):
        count = 1
        raw = dict()
        raw.update(response.meta)
        content = []
        selector = etree.HTML(response.body)
        if "Here's the video" in response.body:
            pass
        elif selector.xpath('//div[@class="article__content"]/child::*')[0].tag == 'section':
            pass
        else:
            title = selector.xpath('//h1/text()')
            raw["title"] = title[0]
            dict_content = {}
            raw["author"] = selector.xpath('//div[@class="contributor"]/a[@class="contributor__link"]/text()')[0]
            time = selector.xpath('//time[@class="byline__pubdate"]/text()')[0].split(',')
            new_string = time[1].strip().split()[0]
            month = self.month_transfer(time[0].strip().split()[0])
            date = time[0].strip().split()[1]
            if len(date) == 2:
                new_string += '-' + month + '-' + date
            else:
                new_string += '-' + month + '-' + '0' + date
            raw["time"] = new_string
            raw['keywords'] = []
            raw['tags'] = ['cherry_matrix']
            raw['publisher'] = ''
            raw['subtitle'] = ''
            raw['content'] = []

            # date = selector.xpath('/html/body/div[1]/section/article/p[@class="create_time"]/text()')
            # self.dict["date"] = date
            # mage = selector.xpath('//div[@class="image-content"]/picture/img/@src')

            image = selector.xpath('//div[@class="image-content"]/picture/source/source/img/@src')
            if image == []:
                image = selector.xpath('//div[@class="image-content"]/picture/img/@src')

            raw["thumbnails"] = [image[0]]

            text = ''
            rich_content = ''
            dict_content['text'] = text
            dict_content['image'] = image[0]
            dict_content['rich_content'] = rich_content
            raw['content'].append(copy.deepcopy(dict_content))
            # new_html = "<html>" + "<body>" + "<h1>" + self.dict["title"][0] + "</h1>" +"<p>" + self.dict["date"][0]+ "</p>"
            for elm in selector.xpath('//div[@class="article__content"]/child::*'):

                if elm.tag == 'p':
                    if elm.attrib != []:
                        b = etree.tostring(elm, method='html', with_tail=False)
                        b = b.decode("utf-8")
                        if "Related Stories" in b:
                            break
                        if "Related Content" in b:
                            break
                        if 'National Suicide Prevention' not in b:
                            text = re.sub('<[^>]*>', '', b)
                            rich_content = ''
                            dict_content['image'] = ''
                            dict_content['text'] = text
                            dict_content['rich_content'] = ''
                            raw['content'].append(copy.deepcopy(dict_content))
                if elm.tag == 'h2':
                    b = etree.tostring(elm, method='html', with_tail=False)
                    b = b.decode("utf-8")
                    text = re.sub('<[^>]*>', '', b)
                    rich_content = ''
                    dict_content['image'] = ''
                    dict_content['text'] = text
                    dict_content['rich_content'] = ''
                    raw['content'].append(copy.deepcopy(dict_content))
                if elm.tag == 'figure':
                    img = elm.xpath('//picture/img/@src')[count]
                    dict_content['image'] = img
                    dict_content['text'] = ''
                    dict_content['rich_content'] = ''
                    raw['content'].append(copy.deepcopy(dict_content))
                    count += 1

        self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(GlamourSpider, self).generate_message(article_info)
        if 'inlinks' in article_info['raw']:
            message['inlinks'] = article_info['raw']['inlinks']
        return message

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

