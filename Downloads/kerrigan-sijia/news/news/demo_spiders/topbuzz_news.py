# -*- coding: utf-8 -*-

import pprint

from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..base_spider import BaseSpider
from test_news_spider import TestNewsSpider
import pprint
import json
import requests
from spider_const import *
import hashlib
import datetime


class TopBuzzSpider(TestNewsSpider):
    name = 'topbuzz_news'
    video_type = 'mp4'
    source_name = 'topbuzz'
    download_delay = 3
    download_maxsize = 104857600
    download_warnsize = 104857600
    default_section = 60 * 60 * 24 * 1 * 365

    topbuzz_host = 'https://i16-tb.isnssdk.com/api/713/stream'
    topbuzz_category = 13
    topbuzz_request_count = 20
    topbuzz_language = 'en'#
    topbuzz_sys_language = 'en'
    topbuzz_sys_region = 'us'#
    topbuzz_platform = 'android'
    topbuzz_tab = 'General'
    topbuzz_device_id = 6535592781073925641

    topbuzz_params = {
        'language': topbuzz_language,
        'sys_language': topbuzz_sys_language,
        'sys_region': topbuzz_sys_region,
        'category': topbuzz_category,
        'count': topbuzz_request_count,
        'tab': topbuzz_tab,
        'device_id': topbuzz_device_id,
        'device_platform': topbuzz_platform
    }

    category_list = [
        [10, 'u.s.'],
        [380, 'top'],
        # [21, 'comedy'],
        # [3, 'entertainment'],
        # [10, 'society'],
        # [341, 'animal'],
        # [19, 'life'],
        # [6, 'sport'],
        # [7, 'vehicle'],
        # [32, 'military'],
        # [8, 'technology'],
        # [12, 'food'],
        # [15, 'game'],
    ]

    channel_list = []

    def __init__(self, *a, **kw):
        super(TopBuzzSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        print (111)
        for topbuzz_category_index, tags in self.category_list:
            self.topbuzz_params['category'] = topbuzz_category_index
            r = requests.get(self.topbuzz_host, params=self.topbuzz_params, verify=False)
            json_data = r.json()
            article_list = json_data['data']['items']
            for item in article_list:
                if item['article_class'] != 'Article':
                    self.logger.info('not Article,continue!')
                    continue
                if 'www.topbuzz.com' in item['url']:
                    self.logger.info('original topbuzz news,continue!')
                    continue
                print(json.dumps(item))

                # if 'subscription' not in item:
                #     self.logger.info('not subscription,continue!')
                #     continue

                raw = dict()
                raw['title'] = item['title']
                raw['thumbnails'] = []
                if 'image_list' in item:
                    for image in item['image_list']:
                        raw['thumbnails'].append(image['url_list'][0]['url'])
                elif 'middle_image' in item:
                    raw['thumbnails'].append(item['middle_image']['url_list'][0]['url'])
                raw['comment_count'] = item['comment_count']
                raw['like_count'] = item['like_count']
                raw['share_count'] = item['share_count']
                raw['view_count'] = item['read_count']
                raw['recommend_count'] = item['recommend_count']
                raw['source_url'] = item['url']
                raw['publisher_icon'] = []
                raw['subtitle'] = ''
                if 'subscription' in item:
                    raw['publisher'] = item['subscription']['source_name']
                    raw['publisher_icon'] = item['subscription']['icon_url']
                else:
                    raw['publisher'] = item['source']
                raw['publish_ts'] = item['publish_time']
                raw['doc_id'] = item['item_id']
                raw['content'] = []
                raw['keywords'] = []
                if 'keywords' in item:
                    for keyword in item['keywords']['data']:
                        raw['keywords'].append(keyword['content'])
                raw['tags'] = []
                try:
                    raw['tags'].append(json.loads(item['log_extra'])['Article Category'])
                except:
                    pass
                raw['extra'] = dict()
                raw['extra']['log_extra'] = item['log_extra']
                self.parse_raw(raw)


        yield Request(
            'https://www.baidu.com/',
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        print (222)
        pass

    def get_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_html_from_raw(self, raw):
        return ''

    def get_raw_tags_from_raw(self, raw):
        tag_list = raw['tags']
        tag_list.insert(0, u'触宝_视频')
        return tag_list

    def title_duplicate(self, ttl):
        return False

    def get_title_from_raw(self, raw):
        return raw['title']

    def get_thumbnails_from_raw(self, raw):
        return raw['thumbnails']

    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    def get_locale_from_raw(self, raw):
        return self.locale

    def get_publish_time_from_raw(self, raw):
        return raw['publish_ts']

    def get_keywords_from_raw(self, raw):
        return []

    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_source_name_from_raw(self, raw):
        return self.source_name

    # 这里不能动，有实际需求复写这个函数
    def get_extra_from_raw(self, raw):
        return raw['extra']

    def get_video_id_from_raw(self, raw):
        return raw['doc_id']

    def get_publisher_from_raw(self, raw):
        return raw['publisher']

    def get_publisher_icon_from_raw(self, raw):
        return raw['publisher_icon']

    def get_publisher_id_from_raw(self, raw):
        return ''

    def get_input_type_from_raw(self, raw):
        return self.input_type

    def get_like_count_from_raw(self, raw):
        return raw['like_count']

    def get_comment_count_from_raw(self, raw):
        return raw['comment_count']

    def get_share_count_from_raw(self, raw):
        return raw['share_count']

    def get_view_count_from_raw(self, raw):
        return raw['view_count']
