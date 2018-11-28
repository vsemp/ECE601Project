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
from scrapy.conf import settings
import re

class TopBuzzSpider(VideoSpider):
    name = 'buzzvideo_single'
    video_type = 'mp4'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    source_name = 'buzzvideo'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    download_maxsize = 104857600
    download_warnsize = 104857600
    default_section = 60 * 60 * 24 * 1 * 365

    content_list = []
    channel_list = []
    browse_times = 0
    browse_limit = 5

    def __init__(self, *a, **kw):
        super(TopBuzzSpider, self).__init__(*a, **kw)
        # channel_list = get_channel_list_with_other_keys(self.source_name, self.locale_full_name)
        # self.channel_list = self.channel_list_filter(channel_list)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def channel_list_filter(self, channel_list):
        temp_list = []
        for each in channel_list:
            # if each['state'] == 1:
            #     continue
            # if each['create_date'] <= (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
            #     continue
            hash_value = settings.getint("hash_value", default=-1)
            hash_total = settings.getint("hash_total", default=-1)

            source_hash = int(hashlib.md5(str(each['source_url'])).hexdigest(), 16)
            if hash_value != -1 and hash_total != -1:
                if source_hash % hash_total != hash_value:
                    continue
                else:
                    self.logger.warning("hash pick!")
            temp_list.append(each)
        # temp_list.reverse()
        return temp_list

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
                    callback=self.parse_page
                )
                self.crawler.engine.crawl(rq, self)

        elif self.channel_list:
            self.browse_times = 0
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

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

        category_parameter = re.findall("user/(.*?)/publish", channel_url)[0]
        raw['category_parameter'] = category_parameter
        url = 'https://i.isnssdk.com/api/491/stream?category=72&category_parameter=%s&tab=Subscribe&device_platform=android' % category_parameter
        self.browse_times = 0
        yield Request(
                    url,
                    meta=raw,
                    dont_filter=True,
                    callback=self.parse_list
                )

    def parse_page(self,response):
        pass
    def parse_list(self, response):
        print "parse_list"
        tjson = json.loads(response.body)
        raw = dict()
        raw.update(response.meta)
        for each in tjson['data']['items']:
            # 过滤掉非视频页
            if 'video' not in each:
                print 'video not in each'
                continue
            if 'url_list' in each['video'] and each['video']['url_list']:
                video_url_list = each['video']['url_list']
                for sb in video_url_list:
                    if sb['text'] == '480p_normal':
                        raw['video'] = sb['urls'][0] if sb['urls'][0].startswith('http://vv.ipstatp.com/') else \
                            sb['urls'][1]
            elif 'url' in each['video']:
                raw['video'] = each['video']['url']
            else:
                continue
            if 'video' not in raw:
                continue
            raw['source_url'] = raw['video']

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
                print e.message
                continue
            self.parse_raw(raw)

        has_more = tjson['data']['has_more']
        self.logger('has_more')
        self.browse_times += self.browse_times
        if has_more and self.browse_times < self.browse_limit:
            max_behot_time = tjson['data']['items'][-1]['behot_time']
            category_parameter = raw['category_parameter']
            url = 'https://i.isnssdk.com/api/491/stream?category=72&category_parameter=%s&tab=Subscribe&max_behot_time=%s&device_platform=android' % (
                category_parameter, max_behot_time)
            yield Request(
                url,
                meta=raw,
                dont_filter=True,
                callback=self.parse_list
            )


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
        return hashlib.md5(str(raw['doc_id'])).hexdigest()

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
