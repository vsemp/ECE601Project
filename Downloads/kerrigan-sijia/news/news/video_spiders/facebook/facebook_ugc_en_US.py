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
    name = 'facebook_ugc_en_US'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_UGC

    def __init__(self, *a, **kw):
        super(FacebookSpider, self).__init__(*a, **kw)
        channel_list = get_channel_list_with_other_keys('facebook_ugc', 'United States of America')
        ugc_list = []
        for each in channel_list:
            ugc_dict = dict()
            try:
                temp_dict = eval(','.join(each['tags']))
                ugc_dict['source_url'] = each['source_url']
                ugc_dict['source_url_id'] = each['source_url_id']
                ugc_dict['state'] = each['state']
                ugc_dict['tags'] = temp_dict['tags']
                ugc_dict['user_id'] = temp_dict['user_id']
                ugc_list.append(ugc_dict)
            except Exception, e:
                self.logger.info("ugc_dict error !!!")
                self.logger.info(e.message)

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
        return "en_US"

    def get_region_from_raw(self, raw):
        if raw['locale'] in [LOCALE_USA_ENGLISH]:
            return REGION_AMERICA
        if raw['locale'] in [LOCALE_INDIA_ENGLISH, LOCALE_INDIA_HINDI, LOCALE_THAILAND_THAI, LOCALE_ARABIA_ARABIC,
                             LOCALE_INDONESIA_INDONESIAN, LOCALE_VIETNAM_VIETNAMESE
                             ]:
            return REGION_ASIA