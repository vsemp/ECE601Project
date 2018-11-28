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


class CnnSpider(OutLinkNews):
    name = 'cnn'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'cnn'
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
        'http://cnn.com/',
    ]

    def __init__(self, *a, **kw):
        super(CnnSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)

        for elm in selector.xpath('//script/text()'):
            # content = etree.tostring(elm)
            if "CNN - Breaking News, Latest News and Videos" in elm:
                match_start = re.search(r"[^a-zA-Z](articleList)[^a-zA-Z]", elm)
                index_start = match_start.start(0) - 1
                match_end = re.search(r"[^a-zA-Z](registryURL)[^a-zA-Z]", elm)
                index_end = match_end.start(0) - 1
                json_body = elm[index_start:index_end]

                for body_json in json.loads(json_body)['articleList']:
                    raw['thumbnails'] = ['https://' + body_json['thumbnail'][2:]]
                    raw['source_url'] = response.urljoin(body_json['uri'])

                    self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        try:
            if raw['thumbnails'] == []:
                pass
            else:
                title = selector.xpath('//title/text()')
                if selector.xpath('//div[@id="main-content"]'):
                    raw['title'] = title[0]
                    raw['time'] = selector.xpath('//meta[@name="pubdate"]/@content')[0].split('T')[0]

                    raw['author'] = selector.xpath('//meta[@name="author"]/@content')[0]

                    raw['keywords'] = []
                    # tags = selector.xpath('//script[@type="text/javascript"]/text()')
                    # print(tags[0])
                    ##addedSingleQuoteJsonStr = re.sub(r"(,?)(\w+?)\s*?:", r"\1'\2':", str(tags[0][35:-8]));
                    # doubleQuotedJsonStr = addedSingleQuoteJsonStr.replace("'", "\"");
                    # print(doubleQuotedJsonStr)

                    # print('11',json.loads(doubleQuotedJsonStr))
                    raw['tags'] = []
                    raw['publisher'] = 'cnn'
                    raw['subtitle'] = ''
                    raw['content'] = []
                    dict_content = {}
                    count = 0
                    for elm in selector.xpath('//div[@class="organism contentStream"]/div/child::*'):
                        if elm.tag == 'p':
                            content = etree.tostring(elm, method='html', with_tail=False)
                            text = re.sub('<[^>]*>', '', content)
                            if text != '':
                                rich_content = ''
                                dict_content['image'] = ''
                                dict_content['text'] = text
                                dict_content['rich_content'] = ''
                                raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'div' and elm.attrib['class'] == 'atom photo':
                            text = ''
                            rich_content = ''
                            img_url = elm.xpath('//div[@class="atom photo"]//img/@src')[count]
                            text = ''
                            rich_content = ''
                            dict_content['image'] = img_url
                            dict_content['text'] = text
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))
                            count += 1



                else:
                    raw['title'] = title[0]
                    raw['time'] = selector.xpath('//meta[@name="pubdate"]/@content')[0].split('T')[0]
                    raw['author'] = selector.xpath('//meta[@name="author"]/@content')[0]
                    # print(raw['author'])
                    raw['keywords'] = []
                    raw['tags'] = []
                    raw['publisher'] = 'cnn'
                    raw['subtitle'] = ''
                    raw['content'] = []
                    dict_content = {}
                    count = 0
                    for elm in selector.xpath('//div[@class="l-container"]/child::*'):
                        if elm.tag == 'div' and elm.attrib['class'] == "el__leafmedia el__leafmedia--sourced-paragraph":
                            text = re.sub('<[^>]*>', '', etree.tostring(elm, method='html', with_tail=False))
                            rich_content = ''
                            dict_content['image'] = ''
                            dict_content['text'] = text
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))

                        elif elm.tag == 'div' and elm.attrib['class'] == "zn-body__paragraph speakable":
                            text = re.sub('<[^>]*>', '', etree.tostring(elm, method='html', with_tail=False))
                            rich_content = ''
                            dict_content['image'] = ''
                            dict_content['text'] = text
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'div' and elm.attrib['class'] == "el__embedded el__embedded--standard":
                            count += 1
                            text = ''
                            rich_content = ''

                            img_url = elm.xpath(
                                '//div[@class="el__embedded el__embedded--standard"]//img/@data-src-small')
                            image = "https:" + img_url[0]
                            text = ''
                            rich_content = ''
                            dict_content['image'] = image
                            dict_content['text'] = text
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'div' and elm.attrib['class'] == "zn-body__paragraph":
                            text = re.sub('<[^>]*>', '', etree.tostring(elm, method='html', with_tail=False))

                            rich_content = ''
                            dict_content['image'] = ''
                            dict_content['text'] = text
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))
                        elif elm.tag == 'div' and elm.attrib['class'] == "el__embedded el__embedded--fullwidth":
                            text = ''
                            rich_content = ''
                            img_url = \
                                elm.xpath('//div[@class="el__embedded el__embedded--fullwidth"]//img/@data-src-small')[
                                    count]
                            image = "https:" + img_url
                            text = ''
                            rich_content = ''
                            dict_content['image'] = image
                            dict_content['text'] = text
                            dict_content['rich_content'] = rich_content
                            raw['content'].append(copy.deepcopy(dict_content))
                            count += 1

                        elif elm.tag == 'div' and elm.attrib['class'] == "zn-body__read-all":
                            for sub_elm in elm.getchildren():
                                if sub_elm.tag == 'div' and sub_elm.attrib['class'] == "zn-body__paragraph":
                                    text = re.sub('<[^>]*>', '',
                                                  etree.tostring(sub_elm, method='html', with_tail=False))
                                    rich_content = ''
                                    dict_content['image'] = ''
                                    dict_content['text'] = text
                                    dict_content['rich_content'] = rich_content
                                    raw['content'].append(copy.deepcopy(dict_content))
                                elif sub_elm.tag == 'div' and sub_elm.attrib[
                                    'class'] == "el__embedded el__embedded--standard":
                                    text = ''
                                    rich_content = ''
                                    img_url = sub_elm.xpath(
                                        '//div[@class="el__embedded el__embedded--standard"]//img/@data-src-small')[
                                        count]
                                    image = "https:" + img_url
                                    text = ''
                                    rich_content = ''
                                    dict_content['image'] = image
                                    dict_content['text'] = text
                                    dict_content['rich_content'] = rich_content
                                    raw['content'].append(copy.deepcopy(dict_content))
                                    count += 1
                                elif sub_elm.tag == 'div' and sub_elm.attrib[
                                    'class'] == "el__embedded el__embedded--fullwidth":
                                    text = ''
                                    rich_content = ''
                                    img_url = sub_elm.xpath(
                                        '//div[@class="el__embedded el__embedded--fullwidth"]//img/@data-src-small')[
                                        count]
                                    image = "https:" + img_url
                                    text = ''
                                    rich_content = ''
                                    dict_content['image'] = image
                                    dict_content['text'] = text
                                    dict_content['rich_content'] = rich_content
                                    raw['content'].append(copy.deepcopy(dict_content))
                                    count += 1

            self.parse_raw(raw)
        except:
            logging.error("article fails to parse")
