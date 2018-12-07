# -*- coding: utf-8 -*-
import copy
import datetime
import hashlib
import re

from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..video_spider_base import VideoSpider
from ...feeds_back_utils import *
from ...spider_const import *


class g9agSpiderBase(VideoSpider):
    name = '9gag_video'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = '9gag'
    input_type = INPUT_TYPE_CRAWL
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
    channel_list = ['https://9gag.com/video?ref=nav']
    browse_times = 0
    browse_limit = 50

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
            self.spider_logger.info(source_url=raw['source_url'], source_state='start',
                                    custom_info='source crawl start')
            # source_url 去重
            if self.is_source_url_exist(self.input_type, raw['source_url']):
                self.logger.info('source_url exists: ' + str(raw['source_url']))
                self.spider_idle()
            else:
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
        channel_url = self.channel_list.pop(0)
        raw = dict()
        raw['tags'] = ["comdy"]
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
        tjson = json.loads(
            re.findall('<script type=\"application/ld\+json\"\>\s*(.*?)\s*\<\/script\>', response.body_as_unicode())[0])
        for sb in tjson['itemListElement']:
            source_url = sb['url']
            raw['source_url'] = source_url
            self.content_list.append(copy.deepcopy(raw))

        next_cursor = re.findall('\"nextCursor\":\"(.*?)\"', response.body_as_unicode())[0]
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
        tjson = json.loads(
            re.findall('GAG.App.loadConfigs\((.*?)\).loadAsynScripts', response.body_as_unicode())[0])
        # try:
        video = tjson['data']['post']['images']['image460sv']['h265Url']
        raw = dict()
        raw.update(response.meta)
        raw['video'] = video #
        raw['duration'] = tjson['data']['post']['images']['image460sv']['duration']#？？？？
        raw['source_url'] = response.url#
        raw['title'] = tjson['data']['post']['title']#
        # raw['tags'].extend(tjson['data']['post']['tags'])
        raw['thumbnails'] = [tjson['data']['post']['images']['image460']['url']]#
        raw['doc_id'] = tjson['data']['post']['id']
        raw['video_width'] = tjson['data']['post']['images']['image460sv']['width']
        raw['video_height'] = tjson['data']['post']['images']['image460sv']['height']
        keywords = []
        for each in tjson['data']['post']['tags']:
            keywords.append(each['key'])
        raw['keywords'] = keywords#
        self.parse_raw(raw)
        # except Exception, e:
        #     self.logger.warning(e)
        #     return

    def generate_message(self, article_info):
        message = super(g9agSpiderBase, self).generate_message(article_info)
        if 'inlinks' in article_info['raw']:
            message['inlinks'] = article_info['raw']['inlinks']#
        return message

    def get_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_html_from_raw(self, raw):
        return ''

    def get_title_from_raw(self, raw):
        return raw['title']

    def get_thumbnails_from_raw(self, raw):
        return raw['thumbnails']

    def get_doc_id_from_raw(self, raw):
        return hashlib.md5(raw['doc_id']).hexdigest()

    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    def get_locale_from_raw(self, raw):
        return self.locale

    def get_content_from_raw(self, raw):
        return ""

    def get_duration_from_raw(self, raw):
        return raw['duration']

    def get_video_from_raw(self, raw):
        return raw['video']

    def get_publish_time_from_raw(self, raw):
        return str(datetime.datetime.now())[:19]

    def get_keywords_from_raw(self, raw):
        return raw['keywords']

    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_video_id_count_from_raw(self, raw):
        return hashlib.md5(raw['video_id']).hexdigest()

    def get_video_height_from_raw(self, raw):
        return raw['video_height']

    def get_video_width_from_raw(self, raw):
        return raw['video_width']

    def get_extra_from_raw(self, raw):
        return {'key': 'extra_key'}

    def get_video_id_from_raw(self, raw):
        return raw['doc_id']

    def get_publisher_from_raw(self, raw):
        return raw['publisher']

    def get_publisher_icon_from_raw(self, raw):
        return raw['publisher_icon']

    def get_publisher_id_from_raw(self, raw):
        return hashlib.md5(raw['publisher_id']).hexdigest()

    def get_source_name_from_raw(self, raw):
        return self.source_name

    def get_video_type_from_raw(self, raw):
        return VIDEO_TYPE_SHORT_VIDEO

    def get_input_type_from_raw(self, raw):
        return self.input_type

