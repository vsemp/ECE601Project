# -*- coding: utf-8 -*-
from facebook_base import FacebookSpiderBase
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


class FacebookSpider(FacebookSpiderBase):
    name = 'facebook_ugc'
    locale = LOCALE_GLOBAL_ENGLISH
    locale_full_name = 'Global'
    video_format = 'mp4'
    input_type = INPUT_TYPE_UGC
    duration_limit = 60 * 20
    browse_limit = 3

    def __init__(self, *a, **kw):
        super(FacebookSpider, self).__init__(*a, **kw)
        channel_list = get_channel_list_with_other_keys("facebook_ugc", self.locale_full_name)
        print (len(channel_list))
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
        locales = source_dict['locales']
        raw = dict()
        raw['tags'] = tags
        raw['extra'] = dict()
        raw['locale'] = locales[0]
        raw['inlinks'] = [channel_url]
        raw['extra']['user_id'] = user_id
        if "locale" in source_dict:
            raw['locale'] = source_dict['locale']
        raw['source_url_id'] = -1
        self.logger.info(channel_url)
        raw['publisher'] = re.findall('www.facebook.com/(.*?)/videos', channel_url)[0]
        url = 'https://m.facebook.com/%s/video_grid/' % raw['publisher']

        self.response_url = url
        yield Request(
            url,
            meta=raw,
            headers=self.hd_mobile,
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
