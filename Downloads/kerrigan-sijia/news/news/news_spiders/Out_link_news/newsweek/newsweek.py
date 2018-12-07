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


class NewsweekSpider(OutLinkNews):
    name = 'newsweek'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'newsweek'
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
        'http://newsweek.com//',
    ]

    def __init__(self, *a, **kw):
        super(NewsweekSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)

        urls = selector.xpath(
            '//div[@class="col2"]/div/div[@id="block-nw-home-featured-story"]/div/div/article/div/div[@class="image"]/a/@href')[
            0]
        urls = response.urljoin(urls)
        thumbnails = selector.xpath(
            '//div[@class="col2"]/div/div[@id="block-nw-home-featured-story"]/div/div/article/div/div/a/picture/img/@src')[
            0]

        urls = selector.xpath(
            '//div[@class="col2"]/div/div[@id="block-nw-home-featured-more"]/div/div/article[@class="clearfix"]/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="col2"]/div/div[@id="block-nw-home-featured-more"]/div/div/article[@class="clearfix"]/div[@class="image"]/a/picture/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="col1"]/div/div[@id="block-nw-home-featured-stories"]/div/div/article/div/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="col1"]/div/div[@id="block-nw-home-featured-stories"]/div/div/article/div/div[@class="image"]/a/picture/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="col3 content-right"]/div/div[@id="block-nw-opinion"]/div/div/ul/li/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="col3 content-right"]/div/div[@id="block-nw-opinion"]/div/div/ul/li/div[@class="image"]/a/picture/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="col3 content-right"]/div/div[@id="block-nw-subfeatured"]/div/div/ul/li/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="col3 content-right"]/div/div[@id="block-nw-subfeatured"]/div/div/ul/li/div[@class="image"]/a/picture/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-nw-magazine-in-magazine"]/div/div/div/div[@class="flex-sm-9"]/div/article[@class="col-sm-4"]/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-nw-magazine-in-magazine"]/div/div/div/div[@class="flex-sm-9"]/div/article[@class="col-sm-4"]/div[@class="image"]/a/picture/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-nw-magazine-in-magazine"]/div/div/div[@class="row bottom"]/article[@class="col-sm-3"]/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-nw-magazine-in-magazine"]/div/div/div[@class="row bottom"]/article[@class="col-sm-3"]/div[@class="image"]/a/picture/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-nw-editors-pick"]/div/div[@class="feature2 flex-sm flex-wrap row"]/article[@class="col-sm-6 col-md-3"]/div/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-nw-editors-pick"]/div/div[@class="feature2 flex-sm flex-wrap row"]/article[@class="col-sm-6 col-md-3"]/div/div[@class="image"]/a/picture/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-fusion-arbitrage-picture-galleries"]/div/div/div[@class="row"]/article[@class="col-sm-4"]/div[@class="image"]/a[@class="image-link article-link"]/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath(
            '//div[@class="page-bottom"]/div[@id="block-fusion-arbitrage-picture-galleries"]/div/div/div[@class="row"]/article[@class="col-sm-4"]/div[@class="image"]/a[@class="image-link article-link"]/picture/img/@src')
        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

        urls = selector.xpath('//div[@class="page-bottom"]/div[@id="block-nw-section-picks"]/div/div/div[@class="row"]/div[@class="col-sm-4"]/div/ul/li/div[@class="image"]/a/@href \
        	                     | //div[@class="page-bottom"]/div[@id="block-nw-section-picks"]/div/div/div[@class="row"]/div[@class="col-sm-4"]/article/div[@class="image"]/a/@href')
        urls = [response.urljoin(url) for url in urls]
        thumbnails = selector.xpath('//div[@class="page-bottom"]/div[@id="block-nw-section-picks"]/div/div/div[@class="row"]/div[@class="col-sm-4"]/article/div[@class="image"]/a/picture/img/@src \
        	                          | //div[@class="page-bottom"]/div[@id="block-nw-section-picks"]/div/div/div[@class="row"]/div[@class="col-sm-4"]/div/ul/li/div[@class="image"]/a/picture/img/@src')

        for index, url in enumerate(urls):
            raw['thumbnails'] = [thumbnails[index]]
            raw['source_url'] = url
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        if raw['thumbnails'] == []:
            pass
        else:
            try:
                title = selector.xpath('//title/text()')
                raw['title'] = title[0]
                raw['time'] = selector.xpath('//meta[@property="article:published_time"]/@content')[0].split('T')[0]
                raw['author'] = selector.xpath('//span[@itemprop="name"]/text()')[0]
                raw['keywords'] = []
                raw['tags'] = []
                content_channels = selector.xpath('//script[@type="text/javascript"]/text()')
                for content_channel in content_channels:
                    if str(content_channel).startswith('dataLayer'):
                        raw['tags'] = json.loads(str(content_channel).split('[')[1][:-2])['content_channel'].split(',')
                raw['publisher'] = 'newsweek'
                raw['subtitle'] = ''
                raw['content'] = []
                dict_content = {}
                count = 0
                for elm in selector.xpath('//div[@class="article-content"]/child::*'):
                    if elm.tag == 'figure' and elm.attrib['itemprop'] == 'image':
                        image = elm.xpath('//img[@itemprop="contentUrl"]/@src')[0]
                        dict_content['image'] = image
                        dict_content['text'] = ''
                        dict_content['rich_content'] = ''
                        raw['content'].append(copy.deepcopy(dict_content))
                    elif elm.tag == 'div' and elm.attrib['class'] == 'article-body':
                        for new_elm in elm.getchildren():
                            if new_elm.tag == 'p':
                                if new_elm.attrib == []:
                                    content = etree.tostring(new_elm, method='html', with_tail=False)
                                    content = content.encode("utf-8")
                                    if "img" in content:
                                        image = new_elm.xpath('//img[@itemprop="contentUrl"]/@src')[count]
                                        count += 1
                                        dict_content['image'] = image
                                        dict_content['text'] = ''
                                        dict_content['rich_content'] = ''
                                        raw['content'].append(copy.deepcopy(dict_content))
                                    elif "href" in content:
                                        text = re.sub('<[^>]*>', '', content)
                                        if text != '':
                                            rich_content = ''
                                            dict_content['image'] = ''
                                            dict_content['text'] = text
                                            dict_content['rich_content'] = ''
                                            raw['content'].append(copy.deepcopy(dict_content))
                                    else:
                                        if re.sub('<[^>]*>', '', content) != '':
                                            rich_content = content
                                            dict_content['image'] = ''
                                            dict_content['text'] = ''
                                            dict_content['rich_content'] = rich_content
                                            raw['content'].append(copy.deepcopy(dict_content))
                    elif elm.tag == 'div' and elm.attrib['class'] == "article-body clearfix":
                        image = elm.xpath('//figure[@itemprop="image"]//img[@itemprop="contentUrl"]/@src')
                        dict_content['image'] = image
                        dict_content['text'] = ''
                        dict_content['rich_content'] = ''
                        raw['content'].append(copy.deepcopy(dict_content))
                        for new_elm in elm.getchildren():
                            if new_elm.tag == 'p':
                                if new_elm.attrib == []:
                                    content = etree.tostring(new_elm, method='html', with_tail=False)
                                    content = content.encode("utf-8")
                                    if "img" in content:
                                        image = new_elm.xpath('//img[@itemprop="contentUrl"]/@src')[count]
                                        count += 1
                                        dict_content['image'] = image
                                        dict_content['text'] = ''
                                        dict_content['rich_content'] = ''
                                        raw['content'].append(copy.deepcopy(dict_content))
                                    elif "href" in content:
                                        text = re.sub('<[^>]*>', '', content)
                                        if text != '':
                                            rich_content = ''
                                            dict_content['image'] = ''
                                            dict_content['text'] = text
                                            dict_content['rich_content'] = ''
                                            raw['content'].append(copy.deepcopy(dict_content))
                                        else:
                                            if re.sub('<[^>]*>', '', content) != '':
                                                rich_content = content
                                                dict_content['image'] = ''
                                                dict_content['text'] = ''
                                                dict_content['rich_content'] = rich_content
                                                raw['content'].append(copy.deepcopy(dict_content))
                self.parse_raw(raw)
            except:
                logging.error("this article fails to scrapy")
