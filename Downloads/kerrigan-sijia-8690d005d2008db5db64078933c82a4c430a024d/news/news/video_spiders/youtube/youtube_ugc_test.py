# -*- coding: utf-8 -*-
from youtube_base import YoutubeSpiderBase
from ...spider_const import *
from ...feeds_back_utils import *
import re
import redis
from scrapy.http import FormRequest, Request
import json
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import lxml
from scrapy.conf import settings
import requests


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_ugc_test'
    locale = LOCALE_GLOBAL_ENGLISH
    locale_full_name = 'Global'
    video_format = 'mp4'
    input_type = INPUT_TYPE_UGC
    duration_limit = 60 * 20
    browse_limit = 2
    need_headers = False

    def __init__(self, *a, **kw):
        super(YoutubeSpider, self).__init__(*a, **kw)
        redis_ugc = redis.Redis('oem02.corp.cootek.com', 6002, 0)
        ugc_dict = redis_ugc.hgetall('ugc_platform_spider_url_list')
        ugc_dict = [{"locale": "en_US", "tags": [], "user_id": "6627260720",
                     "source_url": "https://www.youtube.com/channel/UC_wGW5vQoWjrw-HJyxQK8hw/videos"}]
        ugc_list = []
        self.logger.info(ugc_dict)
        self.logger.info(type(ugc_dict))

        self.channel_list = ugc_dict
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def start_requests(self):
        self.logger.warning(' ugc start_requests')
        source_dict = self.channel_list.pop(0)
        channel_url = source_dict['source_url']
        user_id = source_dict['user_id']
        tags = source_dict['tags']
        locale = source_dict['locale']
        raw = dict()
        raw['tags'] = tags
        raw['extra'] = dict()
        raw['locale'] = locale
        raw['extra']['user_id'] = user_id
        raw['source_url_id'] = -1
        url = '%s?flow=grid&sort=dd&view=0' % channel_url
        self.response_url = url
        self.logger.info(url)

        yield Request(
            url,
            meta=raw,
            headers=self.hd,
            dont_filter=True,
            callback=self.parse_list
        )

    def get_extra_from_raw(self, raw):
        return raw['extra']

    def get_locale_from_raw(self, raw):
        return raw['locale']

    def get_region_from_raw(self, raw):
        if raw['locale'] in [LOCALE_USA_ENGLISH]:
            return REGION_AMERICA
        if raw['locale'] in [LOCALE_INDIA_ENGLISH, LOCALE_INDIA_HINDI, LOCALE_THAILAND_THAI, LOCALE_ARABIA_ARABIC,
                             LOCALE_INDONESIA_INDONESIAN, LOCALE_VIETNAM_VIETNAMESE
                             ]:
            return REGION_ASIA
