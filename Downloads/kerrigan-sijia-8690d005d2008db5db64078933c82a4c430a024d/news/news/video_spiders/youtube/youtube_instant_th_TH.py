from youtube_base import YoutubeSpiderBase
from ...spider_const import *
from pymongo import MongoClient
from scrapy.conf import settings
import hashlib
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import requests
import lxml
import re
from lxml import etree
from ...feeds_back_utils import *
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_instant_th_TH'
    region = REGION_ASIA
    locale = LOCALE_THAILAND_THAI
    locale_full_name = 'Thailand'
    input_type = INPUT_TYPE_CRAWL
    duration_limit = 60 * 60

    channel_list = []

    def __init__(self, *a, **kw):
        super(YoutubeSpiderBase, self).__init__(*a, **kw)
        channel_list = get_channel_list_with_other_keys('youtube_instant', 'Thailand')
        self.channel_list = self.channel_list_filter(channel_list)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def channel_list_filter(self, channel_list):
        temp_list = []
        for each in channel_list:
            source_url = each['source_url']
            if self.is_source_url_exist(self.input_type, source_url):
                self.logger.info('source_url exists: ' + source_url)
                if set_source_url_crawled(each['source_url_id']):
                    self.logger.info('update remote source_url state success')
                else:
                    self.logger.error('update remote source_url state failed')
                continue

            if self.is_source_url_invalid(source_url):
                self.logger.info('source_url invalid: ' + source_url)
                continue

            sp_urls = settings.get("urls", default=[])
            if sp_urls:
                if each['source_url'] not in sp_urls:
                    continue

            if not (settings.getbool('SIM_MODE') or settings.getbool('UPDATE_MODE')):
                if each['state'] == 1:
                    continue
            temp_list.append(each)
        return temp_list

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        source_dict = self.channel_list.pop(0)
        source_url = source_dict['source_url']
        source_url_id = source_dict['source_url_id']
        tags = source_dict['tags']
        state = source_dict['state']
        raw = dict()
        raw['source_url_id'] = source_url_id
        if not settings.getbool('SIM_MODE') and self.input_type == INPUT_TYPE_CRAWL:
            set_source_url_start_crawl(raw['source_url_id'])
        raw['tags'] = tags
        raw['inlinks'] = []
        logging.warning('state == %d' % state)
        yield Request(
            source_url,
            headers=self.hd_page,
            meta=raw,
            dont_filter=True,
            callback=self.parse_page
        )

    def generate_message(self, article_info):
        message = super(YoutubeSpiderBase, self).generate_message(article_info)
        if 'source_url_id' in article_info['raw']:
            message['source_url_id'] = article_info['raw']['source_url_id']
        return message
