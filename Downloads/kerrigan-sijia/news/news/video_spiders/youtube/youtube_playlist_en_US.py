# -*- coding: utf-8 -*-

from youtube_base import YoutubeSpiderBase
from ...spider_const import *
import lxml
from scrapy.conf import settings
from ...feeds_back_utils import *
from scrapy.http import FormRequest, Request
import re
from _struct import *
from _struct import _clearcache
from _struct import __doc__
import hashlib
import copy


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_playlist_en_US'
    source_name = 'youtube_playlist'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'

    def start_requests(self):
        source_dict = self.channel_list.pop(0)
        channel_url = source_dict['source_url']
        source_url_id = source_dict['source_url_id']
        tags = source_dict['tags']
        state = source_dict['state']
        raw = dict()
        raw['tags'] = tags
        raw['inlinks'] = [channel_url]
        raw['source_url_id'] = source_url_id

        url = channel_url
        self.response_url = url
        yield Request(
            url,
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = dict()
        raw.update(response.meta)

        video_list_selectors = '//*[@id="pl-video-table"]/tbody/tr'
        for each in tree.xpath(video_list_selectors):
            raw_url = each.xpath('.//td[@class="pl-video-title"]/a/@href')[0].strip()
            source_url = 'https://www.youtube.com' + raw_url.split('&')[0]
            raw['source_url'] = source_url

            self.content_list.append(copy.deepcopy(raw))
            self.logger.warning(source_url)
        return
