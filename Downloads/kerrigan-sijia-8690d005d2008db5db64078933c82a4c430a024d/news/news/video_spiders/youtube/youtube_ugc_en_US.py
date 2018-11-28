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
import pprint

class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_ugc_en_US'
    locale = LOCALE_GLOBAL_ENGLISH
    locale_full_name = 'United States of America'
    video_format = 'mp4'
    find_youtube_format = '640x360 (medium) .mp4'
    input_type = INPUT_TYPE_UGC
    duration_limit = 60 * 20
    browse_limit = 3

    def __init__(self, *a, **kw):
        super(YoutubeSpiderBase, self).__init__(*a, **kw)
        channel_list = get_channel_list_with_other_keys("youtube_ugc", self.locale_full_name)
        pprint.pprint(channel_list)
        ugc_list = []
        for each in channel_list:
            ugc_list.append(each)
        self.channel_list = ugc_list
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def start_requests(self):
        source_dict = self.channel_list.pop(0)
        channel_url = source_dict['source_url']
        user_id = source_dict['user_id']
        tags = source_dict['tags']
        raw = dict()
        raw['tags'] = tags
        raw['extra'] = dict()
        raw['inlinks'] = [channel_url]
        raw['extra']['user_id'] = user_id
        raw['source_url_id'] = -1
        url = '%s?flow=grid&sort=dd&view=0' % channel_url
        self.response_url = url
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
        return "en_US"

    def get_region_from_raw(self, raw):
        if raw['locale'] in [LOCALE_USA_ENGLISH]:
            return REGION_AMERICA
        if raw['locale'] in [LOCALE_INDIA_ENGLISH, LOCALE_INDIA_HINDI, LOCALE_THAILAND_THAI, LOCALE_ARABIA_ARABIC,
                             LOCALE_INDONESIA_INDONESIAN, LOCALE_VIETNAM_VIETNAMESE
                             ]:
            return REGION_ASIA
