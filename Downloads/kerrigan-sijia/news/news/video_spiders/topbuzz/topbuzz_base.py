# -*- coding: utf-8 -*-
import datetime
import hashlib

import requests
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..video_spider_base import VideoSpider
from ...feeds_back_utils import *
from ...spider_const import *


# TODO 有问题，需要修改
class TopBuzzSpider(VideoSpider):
    name = 'topbuzz_base'
    # download_delay = 3
    # download_timeout = 60
    video_type = 'mp4'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'buzzvideo'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    download_maxsize = 104857600
    download_warnsize = 104857600
    default_section = 60 * 60 * 24 * 1 * 365

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
        [13, 'foryou'],
        [21, 'comedy'],
        [3, 'entertainment'],
        [10, 'society'],
        [341, 'animal'],
        [19, 'life'],
        [6, 'sport'],
        [7, 'vehicle'],
        [32, 'military'],
        [8, 'technology'],
        [12, 'food'],
        [15, 'game'],
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
        for topbuzz_category_index, tags in self.category_list:
            self.topbuzz_params['category'] = topbuzz_category_index
            r = requests.get(self.topbuzz_host, params=self.topbuzz_params)
            json_data = r.json()
            video_list = json_data['data']['items']
            for each in video_list:
                # 过滤掉非视频页
                if 'video' not in each:
                    continue
                if 'url_list' not in each['video']:
                    continue

                raw = dict()
                video_url_list = each['video']['url_list']
                for sb in video_url_list:
                    if sb['text'] == '480p_normal':
                        raw['video'] = sb['urls'][0] if sb['urls'][0].startswith('http://vv.ipstatp.com/') else \
                            sb['urls'][1]
                if 'video' not in raw:
                    continue
                raw['source_url'] = raw['video']
                self.spider_logger.info(source_url=raw['source_url'], source_state='start',
                                        custom_info='source crawl start')
                # source_url 去重
                if self.is_source_url_exist(self.input_type, raw['source_url']):
                    continue

                try:
                    raw['full_content'] = each
                    raw['publisher'] = each['author']['name']

                    raw['publisher_icon'] = [each['author']['avatar']['uri']]
                    raw['doc_id'] = each['video']['id']
                    # # 生成唯一title
                    raw['title'] = each['video']['title']
                    raw['thumbnails'] = [each['large_image']['url_list'][0]['url']]
                    raw['time'] = each['publish_time']
                    log_extra = each['log_extra']
                    raw['tags'] = [tags]
                    raw['log_extra'] = log_extra
                    raw['raw_tags'] = json.loads(log_extra)['Article Category']
                    raw['duration'] = int(each['video']['duration'])
                    raw['publisher_id'] = json.loads(log_extra)['Author ID']
                    raw['publish_time'] = each['publish_time']
                    raw['video_width'] = int(each['video']['width'])
                    raw['video_height'] = int(each['video']['height'])
                    raw['video_id'] = str(each['video']['id'])
                    raw['commentNum'] = int(each['comment_count'])
                except Exception as e:
                    self.spider_logger.error(source_url=raw['source_url'],
                                             custom_info=e.message)
                    continue
                self.parse_raw(raw)
        yield Request(
            'https://www.baidu.com/',
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        pass

    def generate_message(self, article_info):
        message = super(TopBuzzSpider, self).generate_message(article_info)
        if 'inlinks' in article_info['raw']:
            message['inlinks'] = article_info['raw']['inlinks']
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

    def get_video_id_from_raw(self, raw):
        return hashlib.md5(raw['video_id']).hexdigest()

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
        return str(datetime.datetime.fromtimestamp(raw['time']))[:19]

    def get_keywords_from_raw(self, raw):
        return []

    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_source_name_from_raw(self, raw):
        return self.source_name

    def get_video_height_from_raw(self, raw):
        return raw['video_height']

    def get_video_width_from_raw(self, raw):
        return raw['video_width']

    def get_extra_from_raw(self, raw):
        if raw['log_extra'] and raw['full_content']:
            return {'topbuzz_log_extra': raw['log_extra'], 'full_content': raw['full_content']}
        else:
            return {}

    def get_publisher_from_raw(self, raw):
        return raw['publisher']

    def get_publisher_icon_from_raw(self, raw):
        return raw['publisher_icon']

    def get_publisher_id_from_raw(self, raw):
        return hashlib.md5(raw['publisher_id']).hexdigest()

    def get_video_type_from_raw(self, raw):
        return VIDEO_TYPE_SHORT_VIDEO

    def get_input_type_from_raw(self, raw):
        return self.input_type
