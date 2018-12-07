# -*- coding: utf-8 -*-
import copy
import datetime
import hashlib
import re

import scrapy
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from ..base_spider import BaseSpider
import re
from ..feeds_back_utils import *
import pprint


class g9agSpiderBase(BaseSpider):
    name = '9gag_gallery_demo'
    locale_full_name = 'United States of America'
    # find_youtube_format = '640x360 (medium) .webm'
    duration_limit = 60 * 5
    # 确定服务器位置
    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}
    download_delay = 3
    download_maxsize = 104857600 * 5
    download_warnsize = 104857600 * 5
    default_section = 60 * 60 * 24 * 1 * 365
    hd = {'pragma': 'no-cache',
               'cache-control': 'no-cache'}

    response_url = None
    content_list = []
    channel_list = ['https://9gag.com/girl?ref=nav']


    browse_times = 0
    browse_limit = 1

    def extract_cookies(self, cookie):
        """从浏览器或者request headers中拿到cookie字符串，提取为字典格式的cookies"""
        cookies = dict([l.split("=", 1) for l in cookie.split("; ")])
        return cookies

    def __init__(self, *a, **kw):
        super(g9agSpiderBase, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop(0)
            # # source_url 去重
            # if self.is_source_url_exist(self.input_type, raw['source_url']):
            #     self.logger.info('source_url exists: ' + str(raw['source_url']))
            #     self.spider_idle()
            # else:
            self.logger.warning('content_list pop ed')
            rq = Request(
                raw['source_url'],
                headers=self.hd_page,
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
        print (111)
        channel_url = self.channel_list.pop(0)
        raw = dict()
        raw['tags'] = []
        raw['inlinks'] = [channel_url]
        raw['publisher'] = "9gag"
        raw['publisher_id'] = "9gag_id"
        raw['publisher_icon'] = ['https://img-9gag-fun.9cache.com/photo/a3K8b8N_460s.jpg']

        yield Request(
            channel_url,
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        print('parse_list!!!!!')
        print response.url
        f1 = open('http.txt', 'w')
        f1.write(response.body_as_unicode())
        tjson = json.loads(
            re.findall('<script type=\"application/ld\+json\"\>\s*(.*?)\s*\<\/script\>', response.body_as_unicode())[0])
        for sb in tjson['itemListElement']:
            source_url = sb['url']
            raw['source_url'] = source_url
            self.content_list.append(copy.deepcopy(raw))

        next_cursor = re.findall('\"nextCursor\":\"(.*?)\"', response.body_as_unicode())[0]
        print(next_cursor)
        if next_cursor:
            self.browse_times += 1
            if self.browse_times < self.browse_limit:
                next_url = 'https://9gag.com/v1/group-posts/group/video/type/hot?%s' % next_cursor
                yield Request(
                    next_url,
                    meta=raw,
                    headers=self.hd,
                    dont_filter=True,
                    callback=self.parse_list_next,
                )

    def parse_list_next(self, response):
        print (333)
        print('parse_list_next!!!!!')
        raw = dict()
        raw.update(response.meta)
        tjson = json.loads(response.body_as_unicode())

        for sb in tjson['data']['posts']:
            source_url = sb['url']
            raw['source_url'] = source_url
            self.content_list.append(copy.deepcopy(raw))
            print len(self.content_list)

        next_cursor = tjson['data']['nextCursor']
        if next_cursor:
            self.browse_times += 1
            if self.browse_times < self.browse_limit:
                next_url = 'https://9gag.com/v1/group-posts/group/video/type/hot?%s' % next_cursor
                yield Request(
                    next_url,
                    meta=raw,
                    headers=self.hd,
                    dont_filter=True,
                    callback=self.parse_list_next,
                )

    def parse_page(self, response):
        print (444)
        tjson = json.loads(
            re.findall('GAG.App.loadConfigs\((.*?)\).loadAsynScripts', response.body_as_unicode())[0])
        w_tjson = json.dumps(tjson, ensure_ascii=False, encoding='utf8').encode('utf8')
        # f1 = open('json.txt', 'w')
        # f1.write(w_tjson)
        # print w_tjson
        # try:
        page_type =  tjson['data']['post']['type']
        print page_type
        print tjson['data']['post']['sections']
        if page_type == 'Photo':
            raw = dict()
            raw.update(response.meta)
            raw['content'] = []
            content_dict = dict()
            content_dict['image'] = tjson['data']['post']['images']['image700']['url']
            content_dict['text'] = ""
            content_dict['rich_content'] = ""
            raw['content'].append(copy.deepcopy(content_dict))

            raw['source_url'] = response.url
            raw['title'] = tjson['data']['post']['title']
            raw['tags'].extend(tjson['data']['post']['sections'])
            raw['thumbnails'] = [tjson['data']['post']['images']['image460']['url']]
            raw['doc_id'] = tjson['data']['post']['id']
            keywords = []
            for each in tjson['data']['post']['tags']:
                if each in ['gif','video']:
                    continue
                keywords.append(each['key'])
            raw['keywords'] = keywords
            pprint.pprint(raw)
