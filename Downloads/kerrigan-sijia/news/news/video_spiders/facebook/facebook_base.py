# -*- coding: utf-8 -*-
import copy
import datetime
import hashlib
import re

import lxml
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..video_spider_base import VideoSpider
from ...feeds_back_utils import *
from ...spider_const import *
from scrapy.conf import settings


class FacebookSpiderBase(VideoSpider):
    name = 'facebook_base'
    region = REGION_GCT
    locale = LOCALE_USA_ENGLISH
    source_name = 'facebook'
    input_type = INPUT_TYPE_CRAWL
    locale_full_name = 'United States of America'
    # find_youtube_format = '640x360 (medium) .webm'
    duration_limit = 60 * 5
    # 确定服务器位置

    download_delay = 3
    download_maxsize = 104857600 * 5
    download_warnsize = 104857600 * 5
    default_section = 60 * 60 * 24 * 1 * 365
    hd_page = {'pragma': 'no-cache',
               'cache-control': 'no-cache'}

    hd_mobile = {
        'User-Agent': 'okhttp/3.8.0',
        'pragma': 'no-cache',
        'cache-control': 'no-cache'}

    cookie_str = 'datr=VTx9WjLbc5yO-x7ImKheKses; sb=Zzx9Wo7uILDehAwHta9EI1ch; dpr=2; locale=en_US; c_user=100025538571662; xs=21%3AnyafA4OL-Ti7Uw%3A2%3A1526885142%3A-1%3A-1; pl=n; m_pixel_ratio=2; x-referer=eyJyIjoiL1llc0Z1bm55WWVzL3ZpZGVvX2dyaWQvIiwiaCI6Ii9ZZXNGdW5ueVllcy92aWRlb19ncmlkLyIsInMiOiJtIn0%3D; wd=1280x600; act=1527128507279%2F6; fr=07rCjGpXuaLUDhPvL.AWV-mFFmW9cGfc6h9tVtaFgz0n0.BZ1lll.4j.Fr-.0.0.BbBlV0.AWWKce0b; presence=EDvF3EtimeF1527143115EuserFA21B25538571662A2EstateFDutF1527143115438CEchFDp_5f1B25538571662F5CC'
    cookies = ''

    response_url = None
    content_list = []
    channel_list = []
    browse_times = 0
    browse_limit = 2

    def extract_cookies(self, cookie):
        """从浏览器或者request headers中拿到cookie字符串，提取为字典格式的cookies"""
        cookies = dict([l.split("=", 1) for l in cookie.split("; ")])
        return cookies

    def __init__(self, *a, **kw):
        super(FacebookSpiderBase, self).__init__(*a, **kw)
        self.cookies = self.extract_cookies(self.cookie_str)
        channel_list = get_channel_list_with_other_keys(self.source_name, self.locale_full_name)
        self.channel_list = self.channel_list_filter(channel_list)
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
                    dont_filter=True,
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
        raw['publisher'] = re.findall('pg/(.*?)/videos', channel_url)[0]
        url = 'https://m.facebook.com/%s/video_grid/' % raw['publisher']

        self.response_url = url
        yield Request(
            url,
            meta=raw,
            headers=self.hd_mobile,
            dont_filter=True,
            callback=self.parse_list
        )

    def get_icon_url(self, publisher):
        url = 'https://m.facebook.com/%s/?refid=52&__tn__=C-R' % publisher
        print(url)
        r = requests.get(
            url,
            headers=self.hd_mobile,
        )
        tree = lxml.html.fromstring(r.content)
        icon_selector = '//*[@id="m-timeline-cover-section"]/div[1]/div/div[1]/div/a/img/@src'
        icon_url = tree.xpath(icon_selector)[0]
        return icon_url

    def parse_list(self, response):
        print('parse_list')
        print(response.url)
        raw = dict()
        raw.update(response.meta)
        raw['publisher_icon'] = [self.get_icon_url(raw['publisher'])]

        self.logger.warning('icon_url is %s' % raw['publisher_icon'])

        tree = lxml.html.fromstring(response.body)
        table_selector = '//*[@id="root"]/table/tbody/tr/td/div/div/div/div/table'
        tables = tree.xpath(table_selector)
        for each in tables:
            td_selector = 'tbody/tr/td'
            tds = each.xpath(td_selector)
            for sb in tds:
                href_selector = 'div/a/@href'
                try:
                    href_str = sb.xpath(href_selector)[0]
                except IndexError:
                    continue
                page_url = 'https://www.facebook.com/%s/videos/%s/' % (
                    raw['publisher'], re.findall('id=([0-9]+)', href_str)[0])
                raw['source_url'] = page_url
                self.content_list.append(copy.deepcopy(raw))

        next_page_selector = '//*[@id="m_pages_finch_see_more_videos"]/a/@href'
        next_page_url = tree.xpath(next_page_selector)[0]
        next_page_url = "https://www.facebook.com/%s" % next_page_url
        raw['publisher_id'] = re.findall('/(\d+)/videos', next_page_url)[0]
        yield Request(
            next_page_url,
            meta=raw,
            headers=self.hd_mobile,
            dont_filter=True,
            callback=self.parse_browse,
            cookies=self.cookies
        )

    def parse_browse(self, response):
        raw = dict()
        raw.update(response.meta)
        videos = re.findall('id=(\d+)', response.body)
        for each in videos:
            page_url = 'https://www.facebook.com/%s/videos/%s/' % (
                raw['publisher_id'], each)
            raw['source_url'] = page_url
            self.content_list.append(copy.deepcopy(raw))

        self.browse_times += 1
        if self.browse_times > self.browse_limit:
            self.logger.info('browse_times is %s ' % self.browse_times)
            return

        cursor_result = re.findall('cursor=([0-9a-zA-Z\-_]+)', response.body)
        if not cursor_result:
            self.logger.warning('end of pages')
            return

        next_cursor = cursor_result[0]
        next_page_url = "https://www.facebook.com/%s/videos/more/?cursor=%s" % (raw['publisher_id'], next_cursor)
        yield Request(
            next_page_url,
            meta=raw,
            headers=self.hd_mobile,
            dont_filter=True,
            callback=self.parse_browse,
            cookies=self.cookies
        )

    def parse_page(self, response):
        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = dict()
        raw.update(response.meta)
        publisher_selector = '//*[@id="facebook"]/head/meta[@property="og:title"]/@content'
        title_selector = '//*[@id="facebook"]/head/meta[@name="description"]/@content'
        thumbnails_selector = '//*[@id="facebook"]/head/meta[@property="og:image"]/@content'
        video_selector = '//*[@id="facebook"]/body/script[9]/text()'
        video_data = re.findall('videoData:\[(.*?)\]\}', tree.xpath(video_selector)[0].strip())[0] + '}'
        # raw['video_data'] = video_data
        raw['video'] = re.findall('sd_src:\"(.*?)\",', video_data)[0]
        raw['title'] = tree.xpath(title_selector)[0].split('\n')[0]
        raw['subtitle'] = tree.xpath(publisher_selector)[0]
        raw['publisher'] = tree.xpath(publisher_selector)[0]
        raw['source_url'] = response.url
        raw['thumbnails'] = [tree.xpath(thumbnails_selector)[0]]
        raw['doc_id'] = re.findall('videos/([0-9]+)', response.url)[0]
        raw['video_width'] = re.findall('original_width:(.*?),', video_data)[0]
        raw['video_height'] = re.findall('original_height:(.*?),', video_data)[0]

        raw['publisher'] = tree.xpath(publisher_selector)[0]
        raw['publisher_id'] = re.findall('facebook.com/(.*?)/videos', response.url)[0]

        raw['view_count'] = int(re.findall('viewCount:"([0-9,]+)"', body_instance)[0].replace(',', ''))
        raw['like_count'] = int(re.findall('likecount:([0-9,]+)', body_instance)[0].replace(',', ''))
        raw['comment_count'] = int(re.findall('commentcount:([0-9,]+)', body_instance)[0].replace(',', ''))
        raw['share_count'] = int(re.findall('sharecount:([0-9,]+)', body_instance)[0].replace(',', ''))

        raw_duration_str = re.findall('Duration: (.*?) ajaxify', body_instance, re.IGNORECASE)[0]

        raw_hour = re.findall('(\d+) hour', raw_duration_str)
        raw_minute = re.findall('(\d+) minute', raw_duration_str)
        raw_second = re.findall('(\d+) second', raw_duration_str)

        raw['duration'] = 60 * 60 * int(raw_hour[0] if raw_hour else 0) + \
                          60 * int(raw_minute[0] if raw_minute else 0) + \
                          1 * int(raw_second[0] if raw_second else 0)

        self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(FacebookSpiderBase, self).generate_message(article_info)
        if 'inlinks' in article_info['raw']:
            message['inlinks'] = article_info['raw']['inlinks']
        return message

    def get_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_html_from_raw(self, raw):
        return ''

    def get_raw_tags_from_raw(self, raw):
        tag_list = raw['tags']
        tag_list.insert(0, u'触宝_视频')
        return tag_list

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
        return []

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
