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


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_related'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop()
            self.logger.warning('content_list pop ed')
            raw['depth'] = 0
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

    def parse_page(self, response):
        self.logger.info('parse_page')
        self.spider_logger.info(source_url=response.url, source_state='start', custom_info='source crawl start')
        # print response.url
        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = dict()
        raw.update(response.meta)
        if raw['depth'] < 1:
            self.logger.info('depth dig!')
            related_list = '//*[@id="watch-related"]/li'
            for each in tree.xpath(related_list):
                raw_class = each.xpath('.//@class ')[0].strip()
                raw_url = 'https://www.youtube.com' + each.xpath('.//a/@href')[0].strip()
                raw_url = raw_url.split('&')[0]
                raw['depth'] = raw['depth'] + 1
                raw['parent_url'] = response.url
                yield Request(
                    raw_url,
                    headers=self.hd_page,
                    meta=raw,
                    dont_filter=True,
                    callback=self.parse_page
                )

        if raw['depth'] >= 1:
            dedup_key = unpack("<Q", hashlib.md5(raw['parent_url'].encode('utf8')).digest()[:8])[0]
            dedup_key = str(dedup_key)
            raw['extra'] = {'source_related_doc_id': dedup_key}

        if not settings.getbool('SIM_MODE'):
            set_source_url_start_crawl(raw['source_url_id'])
        subtitle_selector = '//*[@id="watch-header"]/div[@id="watch7-user-header"]/div/a/text()'
        thumbnails_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/span[@itemprop="thumbnail"]/link/@href'
        duration_raw_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="duration"]/@content'
        video_id_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="videoId"]/@content'
        title_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="name"]/@content'
        published_date_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="datePublished"]/@content'
        hitcount_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="interactionCount"]/@content'
        width_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="width"]/@content'
        height_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="height"]/@content'
        genre_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="genre"]/@content'

        subtitle_selector = '//*[@id="watch-header"]/div[@id="watch7-user-header"]/div/a/text()'
        publisher_id_selector = '//*[@id="watch-header"]/div[@id="watch7-user-header"]/div/a/@href'
        publisher_icon_selector = '//*[@id="watch-header"]/div[@id="watch7-user-header"]/a/span/span/span[@class="yt-thumb-clip"]/img/@data-thumb'

        raw['title'] = tree.xpath(title_selector)[0].strip()
        raw['subtitle'] = tree.xpath(subtitle_selector)[0]
        raw['source_url'] = response.url
        raw['thumbnails'] = [tree.xpath(thumbnails_selector)[0]]
        raw['time'] = tree.xpath(published_date_selector)[0]
        raw['doc_id'] = tree.xpath(video_id_selector)[0]
        raw['video_width'] = tree.xpath(width_selector)[0]
        raw['video_height'] = tree.xpath(height_selector)[0]
        raw['hit_counts'] = tree.xpath(hitcount_selector)[0]

        raw['publisher_icon'] = [tree.xpath(publisher_icon_selector)[0]]
        raw['publisher'] = tree.xpath(subtitle_selector)[0]
        raw['publisher_id'] = (str(tree.xpath(publisher_id_selector)[0])).split('/')[-1]
        raw['genre'] = tree.xpath(genre_selector)[0].split('&')

        # 正则获取播放时间
        m_value, s_value = \
            re.findall('PT([0-9]+)M([0-9]+)S', tree.xpath(duration_raw_selector)[0])[0]
        # second_value = re.findall('<meta itemprop="duration" content="PT[0-9]+M([0-9]+)S">', body_instance)[0]
        raw['duration'] = int(m_value) * 60 + int(s_value)
        # if raw['duration'] > self.max_duration:
        #     print('duration > %d' % self.max_duration)
        #     return
        self.logger.warning('duration is %s', raw['duration'])

        yield Request(
            raw['source_url'],
            headers=self.hd_page,
            meta=raw,
            dont_filter=True,
            callback=self.parse_video_from_other
        )

    def get_extra_from_raw(self, raw):
        return raw['extra']
