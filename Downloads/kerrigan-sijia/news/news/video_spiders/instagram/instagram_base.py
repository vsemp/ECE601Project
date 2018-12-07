# -*- coding: utf-8 -*-
import copy
import datetime
import hashlib
import json
import re
import urllib2

from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..video_spider_base import VideoSpider
from ...feeds_back_utils import *
from ...spider_const import *


class InstagramBase(VideoSpider):
    name = 'instagram_base'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'instagram'
    input_type = INPUT_TYPE_CRAWL
    locale_full_name = 'United States of America'
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': '',
          'cache-control': 'no-cache'}
    custom_settings = {
        'COOKIES_ENABLED': True
    }

    cookie = 'csrftoken=6AWrzAETRUqrj6vAT9XTdiYqvtXu44r0; ds_user_id=7581755368; rur=FTW; mid=Wwd84wAEAAE4kM9oTLLbGJVQ4Kcg; sessionid=IGSCb27b4f83fc17a1dd80af490380ea0df9c2fdea6cf7bd2526154ebb22f8deacaa%3AFPBc9f9AAAxPunfglGYTcYC0Vl35Y7hd%3A%7B%22_auth_user_id%22%3A7581755368%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_platform%22%3A4%2C%22_token_ver%22%3A2%2C%22_token%22%3A%227581755368%3AmV3VfKnBJjMIqZMLPUK5UJlPDp0YD1Jr%3A9d27ea9159b0225d4c40c098df8e0e91d32ce9f5fedb3b60cc95b27500cd2139%22%2C%22last_refreshed%22%3A1527217380.1436526775%7D; fbm_124024574287414="base_domain=.instagram.com"; mcd=3; urlgen="{\"time\": 1527217379\054 \"103.73.194.8\": 132685}:1fM9lM:bSVmSabFv5J24yKSvmmrbNRNa_Q"'
    cookies = ''

    query_hash = ""
    browse_times = 0
    browse_limit = 5
    content_list = []
    channel_list = []

    def __init__(self, *a, **kw):
        super(InstagramBase, self).__init__(*a, **kw)
        self.ck = self.init_cookies()
        self.cookies = self.extract_cookies(self.cookie)
        self.query_hash = self.init_query_hash()
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
            # if each['tags'] != ['hifit_matrix']:
            #     continue
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
                    headers=self.hd,
                    meta=raw,
                    dont_filter=True,
                    callback=self.parse_page
                )

                self.crawler.engine.crawl(rq, self)

        elif self.channel_list:
            self.browse_times = 0
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def init_query_hash(self):
        print("init_query_hash")

        r = requests.get(
            url='https://www.instagram.com/static/bundles/base/ProfilePageContainer.js/f38773cca89a.js',
            headers=self.hd,
            cookies=self.cookies,
            verify=False
        )

        query_step1 = re.findall("var m=\"([0-9a-zA-Z]+)\"", r.content)[0]
        query_step2 = re.findall("%s([\s\S]*?)queryParams" % query_step1, r.content)[0]
        query_hs = re.findall("queryId:\"([0-9a-zA-Z]+)\"", query_step2)[0]
        return query_hs

    def extract_cookies(self, cookie):
        """从浏览器或者request headers中拿到cookie字符串，提取为字典格式的cookies"""
        cookies = dict([l.split("=", 1) for l in cookie.split("; ")])
        return cookies

    def init_cookies(self):
        ck = '''csrftoken=6AWrzAETRUqrj6vAT9XTdiYqvtXu44r0; ds_user_id=7581755368; rur=FTW; mid=WvEYOQAEAAEUEoRW73EbrxKk130B; sessionid=IGSC4d04a034a96f1df240ba196e1311b9d4958869ce4e236933aad14f1c50d30958%3A0J7ON9nI8t4SuEPGFHsFfKubfUPZiq1u%3A%7B%22_auth_user_id%22%3A7581755368%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_platform%22%3A4%2C%22_token_ver%22%3A2%2C%22_token%22%3A%227581755368%3AmV3VfKnBJjMIqZMLPUK5UJlPDp0YD1Jr%3A9d27ea9159b0225d4c40c098df8e0e91d32ce9f5fedb3b60cc95b27500cd2139%22%2C%22last_refreshed%22%3A1525749817.7874858379%7D; mcd=3; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=NoKJqgec3yWKs9FB75ib30JYfb-foLzvj7Wyvfs4spM.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUExTW4tcHAtRk1MTHVfZGxxT3pBay11dEx4aWgzYjhTUDBPNWx1N1huUGdPMnYwNGttb1U0Q0pQc2ltU2R3QmpwOU5UMEVJbnVHTU9GZWpnNzN5S0N1WGgtaWZ6eW9iN0tvWnlUN0JRTy1iWUYyZW9ZODBpX0hELXo0UlJQbGUzTFAwNUhOZldYWXRyekotMzBpTGxUZVZEdTNZLVN2LUNuRzZPUDB3aWZHRzFrUVlZU1U3aldJSnZSVG9XQlRsaFNUSXpjQkFQeTlxdzllbFp6cnFvWjdUNVhZdGx2bHlNckNpMEcyUDl3Rll1bWtTTFJiUkVSeWFtWmF5UGFscmhTa05NV1ROUl9NRkZ0RVl6XzRBcUFvSzFacGwyai1lV21rYnFkdTBMcVBvRnBkYU5leFlSX3BmMHlUWXJnb2p2N0l2Qy11TFYyaUtaaDFmSkZ6Q0laUCIsImlzc3VlZF9hdCI6MTUyNTgzNTQ3NCwidXNlcl9pZCI6IjEwMDAyNTUzODU3MTY2MiJ9; urlgen="{\"time\": 1525749818\054 \"103.73.194.8\": 132685}:1fGFVb:EVIAG6WEgNeKhYW2oxHHpagGgBM"'''
        ans = {}
        for sb in ck.split(';'):
            ans[sb.split('=', 1)[0].strip()] = sb.split('=', 1)[1].strip()
        return ans

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
        raw['publisher'] = re.findall('https://www.instagram.com/(.*?)/', channel_url)[0]
        yield Request(
            channel_url,
            headers=self.hd,
            # cookies=self.ck,
            dont_filter=True,
            meta=raw,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        print('parse_list!!!!!')
        # soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        tjson = json.loads(re.findall('window._sharedData = (.*?);</script>', response.body_as_unicode())[0])
        self._id = tjson['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        raw['publisher_id'] = tjson['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        raw['publisher_icon'] = [tjson['entry_data']['ProfilePage'][0]['graphql']['user']['profile_pic_url']]
        page_info = tjson['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media'][
            'page_info']
        end_cursor = None
        print('has next page!!!!???')
        print(page_info['has_next_page'])

        if page_info['has_next_page']:
            print('has next page!!!!')
            end_cursor = page_info['end_cursor']
            print(page_info['end_cursor'])

        if end_cursor:
            self.browse_times += 1
            if self.browse_times < self.browse_limit:
                variables = '{"id":"%s","first":12,"after":"%s"}' % (self._id, end_cursor)
                variables = urllib2.quote(variables)
                next_url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s' % (
                    self.query_hash, variables)
                print(next_url)

                yield Request(
                    next_url,
                    headers=self.hd,
                    dont_filter=True,
                    callback=self.parse_list_next,
                    cookies=self.cookies,
                    meta=raw

                )

        for sb in tjson['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
            is_video = sb['node']['is_video']
            if not is_video:
                continue
            source_url = 'https://www.instagram.com/p/%s/' % sb['node']['shortcode']
            # title = sb['node']['caption']
            # thumbnails = sb['node']['display_src']
            # ts = sb['node']['date']
            # if not (source_url and title and thumbnails and ts):
            #     continue
            raw['source_url'] = source_url

            self.content_list.append(copy.deepcopy(raw))

            # break

    def parse_list_next(self, response):
        raw = dict()
        raw.update(response.meta)
        print('parse_list_next')
        tjson = json.loads(response.body_as_unicode())['data']['user']['edge_owner_to_timeline_media']
        page_info = tjson['page_info']
        end_cursor = None
        if page_info['has_next_page']:
            end_cursor = page_info['end_cursor']
        if end_cursor:
            self.browse_times += 1
            if self.browse_times < self.browse_limit:
                variables = '{"id":"%s","first":12,"after":"%s"}' % (self._id, end_cursor)
                variables = urllib2.quote(variables)
                next_url = 'https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%s' % variables
                yield Request(
                    next_url,
                    headers=self.hd,
                    dont_filter=True,
                    meta=raw,
                    callback=self.parse_list_next,
                    cookies=self.ck
                )
        for tnode in tjson['edges']:
            sb = tnode['node']
            is_video = sb['is_video']
            if not is_video:
                continue
            source_url = 'https://www.instagram.com/p/%s/' % sb['shortcode']
            title = sb['edge_media_to_caption']['edges'][0]['node']['text']
            thumbnails = sb['display_url']
            ts = sb['taken_at_timestamp']
            if not (source_url and title and thumbnails and ts):
                continue
            raw['source_url'] = source_url
            # raw['title'] = title
            # raw['thumbnails'] = [thumbnails]
            self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        print('parse_content')
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        try:
            video = soup.find('meta', attrs={'property': 'og:video'}).attrs['content']
        except Exception, e:
            self.logger.warning(e)
            self.logger.warning('no video')
            return
        raw = dict()
        raw.update(response.meta)
        raw['video'] = video
        raw['duration'] = -1
        raw['source_url'] = response.url
        raw['title'] = soup.find('meta', attrs={'property': 'og:title'}).attrs['content'].split('\n')[0]
        raw['thumbnails'] = [soup.find('meta', attrs={'property': 'og:image'}).attrs['content']]
        print response.url
        raw['doc_id'] = re.findall('https://www.instagram.com/p/(.*?)/', response.url)[0]
        raw['video_width'] = soup.find('meta', attrs={'property': 'og:video:width'}).attrs['content'].split('\n')[0]
        raw['video_height'] = soup.find('meta', attrs={'property': 'og:video:height'}).attrs['content'].split('\n')[0]

        yield self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(InstagramBase, self).generate_message(article_info)
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
        return 30

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
        return VIDEO_TYPE_SMALL_VIDEO

    def get_input_type_from_raw(self, raw):
        return self.input_type
