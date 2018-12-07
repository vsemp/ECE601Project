# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from abc import ABCMeta, abstractmethod, abstractproperty
import json
from ..base_spider import BaseSpider
import struct
import hashlib
from spider_const import *
import time
from collections import OrderedDict


class TestNewsSpider(BaseSpider):
    data_source_type = DATA_SOURCE_TYPE_NEWS
    input_type = INPUT_TYPE_CRAWL
    region = REGION_GCT
    locale = LOCALE_USA_ENGLISH
    process_mode = 'normal_mode'

    article_info_keys = ['doc_id', 'account', 'article_class', 'crawl_id', 'crawl_time', 'extra',
                         'input_type', 'keywords', 'locale', 'region', 'process_mode', 'publish_time',
                         'publisher',
                         'publisher_id', 'share_count', 'source_name', 'source_url', 'tags', 'thumbnails', 'title']

    news_info_keys = ['comment_count', 'content', 'view_count', 'like_count', 'page_type', 'publisher_icon',
                      'subtitle']

    article_info_keys.extend(news_info_keys)

    # def parse_raw(self, raw):
    #     print(json.dumps(raw))

    def parse_raw(self, raw):
        self.logger.warning('parse_raw!!!')
        article_info = self.generate_article_info(raw)
        article_info.pop('raw')

        print(json.dumps(OrderedDict(sorted(article_info.items(), key=lambda k: k[0]))))

    def generate_article_info(self, raw):
        article_info = dict()
        for key in self.article_info_keys:
            article_info[key] = getattr(self, 'get_%s_from_raw' % key)(raw)
            if article_info[key] is None:
                raise Exception('%s is None' % key)
                return None
            raw[key] = article_info[key]
        article_info['raw'] = raw
        return article_info

    def get_account_from_raw(self, raw):
        return '%s%s-%s' % ('test_', self.source_name, self.get_doc_id(raw['source_url']))

    def get_doc_id(self, source_url):
        dedup_key = struct.unpack("<Q", hashlib.md5(source_url.encode('utf8')).digest()[:8])[0]
        return str(dedup_key)

    @abstractmethod
    def get_doc_id_from_raw(self, raw):
        return self.get_doc_id(raw['source_url'])

    @abstractmethod
    def get_extra_from_raw(self, raw):
        return {}

    def get_html_from_raw(self, raw):
        return raw['response'].body_as_unicode()

    @abstractmethod
    def get_keywords_from_raw(self, raw):
        pass

    def get_locale_from_raw(self, raw):
        return self.locale

    def get_region_from_raw(self, raw):
        return self.region

    def get_process_mode_from_raw(self, raw):
        return self.process_mode

    @abstractmethod
    def get_publish_time_from_raw(self, raw):
        return raw['publish_time']

    @abstractmethod
    def get_publisher_from_raw(self, raw):
        return raw['publisher']

    @abstractmethod
    def get_publisher_id_from_raw(self, raw):
        return raw['publisher_id']

    @abstractmethod
    def get_source_name_from_raw(self, raw):
        return self.source_name

    @abstractmethod
    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    @abstractmethod
    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_thumbnails_from_raw(self, raw):
        return []

    @abstractmethod
    def get_title_from_raw(self, raw):
        return raw['title']

    @abstractmethod
    def get_article_class_from_raw(self, raw):
        return DATA_SOURCE_TYPE_NEWS

    @abstractmethod
    def get_input_type_from_raw(self, raw):
        pass

    @abstractmethod
    def get_share_count_from_raw(self, raw):
        pass

    def get_crawl_id_from_raw(self, raw):
        return 'test_crawl_id'

    def get_page_type_from_raw(self, raw):
        return 'news'

    def get_view_count_from_raw(self, raw):
        return -1

    def get_like_count_from_raw(self, raw):
        return -1

    def get_comment_count_from_raw(self, raw):
        return -1

    def get_share_count_from_raw(self, raw):
        return -1

    def get_content_from_raw(self, raw):
        return raw['content']

    @abstractmethod
    def get_thumbnails_from_raw(self, raw):
        return raw['thumbnails']

    @abstractmethod
    def get_publisher_icon_from_raw(self, raw):
        return raw['publisher_icon']

    @abstractmethod
    def get_subtitle_from_raw(self, raw):
        return raw['subtitle']

    def get_article_class_from_raw(self, raw):
        return self.data_source_type

    def get_input_type_from_raw(self, raw):
        return self.input_type

    def get_crawl_time_from_raw(self, raw):
        return int(time.time())
