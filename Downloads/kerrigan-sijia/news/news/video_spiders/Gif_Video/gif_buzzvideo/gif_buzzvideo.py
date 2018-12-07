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
import base64
import demjson
from ..gif_video_base import Gif_Video_Spider
from ....feeds_back_utils import *
from ....spider_const import *
import hashlib
import datetime


class Gif_topbuzzSpider(Gif_Video_Spider):
    name = 'gif_topbuzz'
    download_delay = 3
    download_timeout = 60
    video_type = 'mp4'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'buzzvideo'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    download_maxsize = 104857600
    download_warnsize = 104857600
    default_section = 60 * 60 * 24 * 1 * 365

    browse_limit = 5


    topbuzz_host = 'https://i.isnssdk.com/api/572/stream'
    topbuzz_category = 13
    topbuzz_request_count = 20
    topbuzz_language = 'en'
    topbuzz_sys_language = 'en'
    topbuzz_sys_region = 'us'
    topbuzz_platform = 'android'
    topbuzz_tab = 'Video'
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
        [52, 'gif'],
    ]

    channel_list = []

    def __init__(self, *a, **kw):
        super(Gif_topbuzzSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        for topbuzz_category_index, tags in self.category_list:

            self.topbuzz_params['category'] = topbuzz_category_index
            for i in range(100):

                ta = ['23.95.140.220:13228', '23.95.140.193:13228', '23.95.140.162:13228', '23.95.140.119:13228',
                      '23.95.140.111:13228', '23.95.140.22:13228', '23.95.139.115:13228', '23.95.139.93:13228',
                      '23.95.139.70:13228', '23.95.140.11:13228', '23.95.140.96:13228', '23.95.139.19:13228',
                      '198.23.195.16:13228', '192.210.248.207:13228', '192.210.248.100:13228', '192.210.248.86:13228',
                      '192.210.248.18:13228', '192.210.248.120:13228', '192.210.248.73:13228', '192.210.248.62:13228',
                      '198.23.195.104:13228', '198.23.195.47:13228',
                      '198.23.195.163:13228', '192.210.248.247:13228', '198.23.195.58:13228']
                tp = random.choice(ta)
                proxies = {
                    'http': 'http://{}'.format(tp),
                    'https': 'http://{}'.format(tp)
                }

                r = requests.get(self.topbuzz_host, params=self.topbuzz_params, proxies=proxies, verify=False)

                json_data = r.json()
                video_list = json_data['data']['items']

                for each in video_list:
                    raw = dict()

                    try:

                        raw['full_content'] = each
                        raw['publisher'] = each['author']['name']
                        raw['publisher_icon'] = [each['author']['avatar']['uri']]
                        raw['doc_id'] = each['video']['id']
                        raw['title'] = each['video']['title']
                        raw['thumbnails'] = [each['large_image']['url_list'][0]['url']]

                        raw['time'] = each['publish_time']
                        log_extra = each['log_extra']
                        raw['log_extra'] = log_extra
                        raw['tags'] = json.loads(log_extra)['Article Category']
                        raw['duration'] = int(each['video']['duration'])
                        raw['publisher_id'] = json.loads(log_extra)['Author ID']
                        raw['publish_time'] = each['publish_time']
                        raw['video_width'] = int(each['video']['width'])
                        raw['video_height'] = int(each['video']['height'])
                        raw['video_id'] = str(each['video']['id'])
                        raw['video'] = each['url']
                        raw['source_url'] = raw['video']
                        if self.is_source_url_exist(self.input_type, raw['source_url']):
                            continue
                        raw['comment_count'] = int(each['comment_count'])
                        raw['like_count'] = int(each['like_count'])
                        raw['view_count'] = int(each['view_count'])
                        raw['share_count'] = int(each['share_count'])

                    except Exception as e:
                        logging.error("this article fails to parse")
                        continue
                    self.parse_raw(raw)

        yield Request(
            'https://www.baidu.com/',
            dont_filter=True,
            callback=self.parse_list)

    def get_comment_count_from_raw(self, raw):
        return raw['comment_count']

    def get_share_count_from_raw(self, raw):
        return raw['share_count']

    def get_view_count_from_raw(self, raw):
        return raw['view_count']

    def get_like_count_from_ra(self, raw):
        return raw['like_count']
