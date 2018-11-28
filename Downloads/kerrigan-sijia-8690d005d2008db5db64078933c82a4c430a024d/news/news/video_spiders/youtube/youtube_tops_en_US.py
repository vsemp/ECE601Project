# -*- coding: utf-8 -*-
import datetime
import hashlib
import re
from urllib import unquote

import lxml
from scrapy import signals
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..video_spider_base import VideoSpider
from ...feeds_back_utils import *
from ...spider_const import *


class YoutubeSpider(VideoSpider):
    name = 'youtube_tops_en_US'
    locale = LOCALE_USA_ENGLISH
    # 确定服务器位置
    region = REGION_AMERICA
    download_delay = 3
    video_type = 'mp4'
    download_maxsize = 104857600 * 5
    download_warnsize = 104857600 * 5
    # 不做時間的限制
    default_section = 60 * 60 * 24 * 1 * 365
    hd = {'pragma': 'no-cache',
          'User-Agent': '',
          'cache-control': 'no-cache'}
    response_url = None
    content_list = []
    channel_list = []
    browse_times = 0

    def __init__(self, *a, **kw):
        super(YoutubeSpider, self).__init__(*a, **kw)
        channel_list = get_channel_list_with_other_keys('youtube_tops', 'United States of America')
        self.channel_list = self.channel_list_filter(channel_list)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def channel_list_filter(self, channel_list):
        temp_list = []
        for each in channel_list:
            if not (settings.getbool('SIM_MODE') or settings.getbool('UPDATE_MODE')):
                if each['state'] == 1:
                    continue
            if each['create_date'] <= (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
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
        raw['tags'] = tags
        raw['source_url_id'] = source_url_id
        logging.warning('state == %d' % state)
        yield Request(
            source_url,
            headers=self.hd,
            meta=raw,
            dont_filter=True,
            callback=self.parse_page
        )

    def parse_page(self, response):
        self.spider_logger.info(source_url=response.url, source_state='start', custom_info='source crawl start')
        # print response.url
        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = dict()
        raw.update(response.meta)
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
        raw['video_id'] = raw['doc_id']
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
        yield Request(
            raw['source_url'],
            headers=self.hd,
            meta=raw,
            dont_filter=True,
            callback=self.parse_video_from_other
        )

    def parse_video_from_other(self, response):
        target_url = "https://www.findyoutube.net/result"

        post_dict = {
            "url": response.url,
            "submit": "Download"
        }
        r = requests.post(target_url, data=post_dict)

        body_instance = r.content.replace('amp;', '')
        tree = lxml.html.fromstring(body_instance)

        # video_selector = '/html/body/div[2]/div/div[1]/table/tbody/tr[3]/td[3]/button/a/@href'

        tr_containers = tree.xpath('//*[@id="videos_modal"]/div/div/div[2]/table/tbody/tr')

        for each in tr_containers:
            temp_str = each.xpath('td[1]/text()')[0].strip()
            if temp_str == '640x360 (medium) .mp4':
                raw = dict()
                raw.update(response.meta)
                raw['video'] = each.xpath('td[3]/button/a/@href')[0]
                self.logger.warning("find target: " + temp_str)
                yield self.parse_raw(raw)

    def parse_video(self, response):
        def _parse_stream_map(text):
            videoinfo = {
                "itag": [],
                "url": [],
                "quality": [],
                "fallback_host": [],
                "s": [],
                "type": []
            }
            videos = text.split(",")
            videos = [video.split("&") for video in videos]
            for video in videos:
                for kv in video:
                    key, value = kv.split("=")
                    videoinfo.get(key, []).append(unquote(value))
            return videoinfo

        ENCODING = {
            # Flash Video
            5: ["flv", "240p", "Sorenson H.263", "N/A", "0.25", "MP3", "64"],
            6: ["flv", "270p", "Sorenson H.263", "N/A", "0.8", "MP3", "64"],
            34: ["flv", "360p", "H.264", "Main", "0.5", "AAC", "128"],
            35: ["flv", "480p", "H.264", "Main", "0.8-1", "AAC", "128"],

            # 3GP
            36: ["3gp", "240p", "MPEG-4 Visual", "Simple", "0.17", "AAC", "38"],
            13: ["3gp", "N/A", "MPEG-4 Visual", "N/A", "0.5", "AAC", "N/A"],
            17: ["3gp", "144p", "MPEG-4 Visual", "Simple", "0.05", "AAC", "24"],

            # MPEG-4
            18: ["mp4", "360p", "H.264", "Baseline", "0.5", "AAC", "96"],
            22: ["mp4", "720p", "H.264", "High", "2-2.9", "AAC", "192"],
            37: ["mp4", "1080p", "H.264", "High", "3-4.3", "AAC", "192"],
            38: ["mp4", "3072p", "H.264", "High", "3.5-5", "AAC", "192"],
            82: ["mp4", "360p", "H.264", "3D", "0.5", "AAC", "96"],
            83: ["mp4", "240p", "H.264", "3D", "0.5", "AAC", "96"],
            84: ["mp4", "720p", "H.264", "3D", "2-2.9", "AAC", "152"],
            85: ["mp4", "1080p", "H.264", "3D", "2-2.9", "AAC", "152"],

            # WebM
            43: ["webm", "360p", "VP8", "N/A", "0.5", "Vorbis", "128"],
            44: ["webm", "480p", "VP8", "N/A", "1", "Vorbis", "128"],
            45: ["webm", "720p", "VP8", "N/A", "2", "Vorbis", "192"],
            46: ["webm", "1080p", "VP8", "N/A", "N/A", "Vorbis", "192"],
            100: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "128"],
            101: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "192"],
            102: ["webm", "720p", "VP8", "3D", "N/A", "Vorbis", "192"]
        }

        ENCODING_KEYS = (
            'extension',
            'resolution',
            'video_codec',
            'profile',
            'video_bitrate',
            'audio_codec',
            'audio_bitrate'
        )

        def _extract_fmt(text):
            itag = re.findall('itag=(\d+)', text)
            if itag and len(itag) is 1:
                itag = int(itag[0])
                attr = ENCODING.get(itag, None)
                if not attr:
                    return itag, None
                return itag, dict(zip(ENCODING_KEYS, attr))

        content = response.body_as_unicode()
        try:
            player_conf = content[18 + content.find("ytplayer.config = "):]
            bracket_count = 0
            i = 0
            for i, char in enumerate(player_conf):
                if char == "{":
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        break
            else:
                self.logger.warning("Cannot get JSON from HTML")

            index = i + 1
            data = json.loads(player_conf[:index])
            # self.logger.warning(data)
        except Exception, e:
            self.logger.warning(e)
            return

        stream_map = _parse_stream_map(data["args"]["url_encoded_fmt_stream_map"])

        video_urls = stream_map["url"]
        raw = dict()
        raw.update(response.meta)
        for i, url in enumerate(video_urls):
            try:
                fmt, fmt_data = _extract_fmt(url)
                if fmt_data["extension"] == "mp4" and fmt_data["profile"] == "Baseline":
                    raw['video'] = url
                    self.logger.warning(url)
                    break
            except KeyError:
                continue
        # self.logger.warning(raw)

        for request in self.parse_raw(raw):
            yield request

    def get_title_from_raw(self, raw):
        return raw['title']

    def get_subtitle_from_raw(self, raw):
        return raw['subtitle']

    def get_thumbnails_from_raw(self, raw):
        return raw['thumbnails']

    def get_doc_id_from_raw(self, raw):
        return hashlib.md5(raw['doc_id']).hexdigest()

    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    def get_html_from_raw(self, raw):
        return ''

    def get_content_from_raw(self, raw):
        return []

    def get_duration_from_raw(self, raw):
        return raw['duration']

    def get_video_from_raw(self, raw):
        return raw['video']

    def get_source_url_id_from_raw(self, raw):
        logging.warning(raw['source_url_id'])
        return raw['source_url_id']

    def get_raw_tags_from_raw(self, raw):
        tag_list = raw['tags']
        tag_list.insert(0, u'触宝_视频')
        return tag_list

    def get_chinese_name(self, sb):
        tmd5 = hashlib.md5(sb).hexdigest()
        ans = ''
        for ind in range(29):
            tmp = int(tmd5[ind: ind + 4], 16)
            if 19968 <= tmp <= 40869:
                ans += unichr(tmp)
        if len(ans) >= 3:
            return ans[-3:]
        return u'美女如云'

    def title_contain_chinese(self, sb):
        ans = re.findall(ur'[\u4e00-\u9fa5]+', sb)
        if not ans:
            return False
        tmax = max(map(lambda x: len(x), ans))
        if tmax < 2:
            return False
        return True

    def get_locale_from_raw(self, raw):
        return 'en_US'

    def get_extra_from_raw(self, raw):
        return {}

    def get_video_id_from_raw(self, raw):
        return raw['video_id']

    def get_video_height_from_raw(self, raw):
        return raw['video_height']

    def get_video_width_from_raw(self, raw):
        return raw['video_width']

    def get_publisher_from_raw(self, raw):
        return raw['publisher']

    def get_source_name_from_raw(self, raw):
        return 'youtube'

    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_keywords_from_raw(self, raw):
        return []

    def get_publish_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_publisher_id_from_raw(self, raw):
        return raw['publisher_id']
