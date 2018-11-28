# -*- coding: utf-8 -*-
import copy
import datetime
import hashlib
import re
from urllib import unquote

import lxml
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..video_spider_base import VideoSpider
from ...feeds_back_utils import *
from ...spider_const import *
import random
import commands
from tools.statistic import YoutubeStatistic
from tools.YoutubeComments import YoutubeCommentUtil
import traceback


class YoutubeSpiderBase(VideoSpider):
    name = 'youtube_base'
    region = REGION_GCT
    locale = LOCALE_USA_ENGLISH
    source_name = 'youtube'
    input_type = INPUT_TYPE_CRAWL
    locale_full_name = 'United States of America'
    # find_youtube_format = '640x360 (medium) .webm'
    duration_limit = 60 * 5
    matrix_duration_limit = 60 * 10
    # 确定服务器位置
    download_delay = 3
    download_maxsize = 104857600 * 5
    download_warnsize = 104857600 * 5
    default_section = 60 * 60 * 24 * 1 * 365
    hd = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'pragma': 'no-cache',
        'cache-control': 'no-cache'
    }

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}
    response_url = None
    content_list = []
    channel_list = []
    browse_times = 0
    browse_limit = 1

    def __init__(self, *a, **kw):
        super(YoutubeSpiderBase, self).__init__(*a, **kw)
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

            sp_urls = settings.get("urls", default=[])
            if sp_urls:
                if each['source_url'] not in sp_urls:
                    continue

            source_hash = int(hashlib.md5(str(each['source_url'])).hexdigest(), 16)
            if hash_value != -1 and hash_total != -1:
                if source_hash % hash_total != hash_value:
                    continue
                else:
                    self.logger.warning("hash pick!")
            temp_list.append(each)
        # temp_list.reverse()

        self.logger.info(temp_list)
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
            elif self.is_source_url_invalid(raw['source_url']):
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
        raw = dict()
        raw['tags'] = tags
        raw['inlinks'] = [channel_url]
        raw['source_url_id'] = source_url_id
        raw['duration_limit'] = self.duration_limit

        for tag in tags:
            if 'matrix' in tag or 'hifit' in tag or 'cherry' in tag:
                raw['duration_limit'] = self.matrix_duration_limit
                break

        url = '%s?flow=grid&sort=dd&view=0' % channel_url
        self.response_url = url
        yield Request(
            url,
            meta=raw,
            headers=self.hd,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        file("/home/xinyu.du/debug.txt", 'w').write(response.body_as_unicode().encode('utf-8'))

        try:
            subtitle = soup.find('div', attrs={'id': 'microformat'}).get_text().replace(' - YouTube', '').strip()
        except Exception, e:
            self.logger.warning(e)
            self.logger.warning('no subtitle!')
            return
            time.sleep(5)
            yield Request(
                response.url,
                meta=raw,
                headers=self.hd,
                dont_filter=True,
                callback=self.parse_list
            )
            return
        tcnt = None
        for sp in soup.find_all('script'):
            if 'window["ytInitialData"]' in sp.get_text():
                tcnt = sp.get_text()
        ptn = re.compile('(\{"responseContext".*?\}\}\});.*?window\["ytInitialPlayerResponse"\]', re.S)

        tjson = json.loads(ptn.findall(tcnt)[0].strip())
        tcontent = {}
        for sb in tjson['contents']['twoColumnBrowseResultsRenderer']['tabs']:
            try:
                tcontent = \
                    sb['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer'][
                        'contents'][
                        0]['gridRenderer']['items']
            except:
                continue
        for sb in tcontent:
            data = sb['gridVideoRenderer']
            title = data['title']['simpleText']
            raw_thumbnails = 'https://' + data['thumbnail']['thumbnails'][-1]['url'].split('//')[-1]
            thumbnails = re.findall('(.*?)\?', raw_thumbnails)[0]
            hit_counts = re.sub('[\s,]|views', '', data['viewCountText']['simpleText'])
            doc_id = data['navigationEndpoint']['watchEndpoint']['videoId']
            duration = self.duration_gen(
                data['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['text']['simpleText'])

            if not (title and thumbnails and hit_counts and doc_id):
                continue
            if duration > raw['duration_limit']:
                self.logger.warning('seconds > %s' % raw['duration_limit'])
                continue
            source_url = 'https://www.youtube.com/watch?v=%s' % doc_id

            raw['thumbnails'] = [thumbnails]
            raw['hit_counts'] = hit_counts
            raw['doc_id'] = doc_id
            raw['duration'] = duration
            raw['subtitle'] = subtitle
            raw['source_url'] = source_url
            self.content_list.append(copy.deepcopy(raw))
            self.logger.warning(title)
            self.logger.warning(source_url)

            # break
            # return
            # for k in sb['gridVideoRenderer']:
            #     self.logger.warning(k)
            #     self.logger.warning(sb['gridVideoRenderer'][k]

        try:
            ctoken, itct = \
                re.findall('"continuation":"(.*?)","clickTrackingParams":"(.*?)"', response.body_as_unicode())[0]
        except Exception, e:
            self.logger.warning(e)
            return
        browse_url = 'https://www.youtube.com/browse_ajax?ctoken=%s&itct=%s' % (ctoken, itct)
        hd = {
            # 'cookie': 'VISITOR_INFO1_LIVE=jrLlcFZyJd0; YSC=3Qf7FrlhMOE; PREF=f1=50000000&f4=4000000&cvdm=grid&hl=en',
            'x-spf-previous': self.response_url,
            'x-spf-referer': self.response_url,
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20171018',
            'x-youtube-page-cl': '172568519',
            'x-youtube-page-label': 'youtube.ytfe.desktop_20171018_0_RC0',
            'x-youtube-variants-checksum': 'cc5602af9e6709df9857fcf09938a6dc',
        }
        yield Request(
            browse_url,
            headers=hd,
            dont_filter=True,
            meta=raw,
            callback=self.parse_browse
        )

    def parse_browse(self, response):
        raw = dict()
        raw.update(response.meta)
        try:
            itct = json.loads(response.body_as_unicode())[1]['response']['continuationContents']['gridContinuation'][
                'continuations'][0]['nextContinuationData']['clickTrackingParams']
            ctoken = json.loads(response.body_as_unicode())[1]['response']['continuationContents']['gridContinuation'][
                'continuations'][0]['nextContinuationData']['continuation']
            self.logger.warning(itct)
            if not itct:
                return
        except Exception, e:
            self.logger.warning('no itct')
            return
        try:
            tjson = json.loads(response.body_as_unicode())[1]['response']['continuationContents']['gridContinuation'][
                'items']
        except Exception, e:
            self.logger.warning(e)
            return
        for sb in tjson:
            data = sb['gridVideoRenderer']
            title = data['title']['simpleText']
            raw_thumbnails = 'https://' + data['thumbnail']['thumbnails'][-1]['url'].split('//')[-1]
            thumbnails = re.findall('(.*?)\?', raw_thumbnails)[0]
            hit_counts = re.sub('[\s,]|views', '', data['viewCountText']['simpleText'])
            doc_id = data['navigationEndpoint']['watchEndpoint']['videoId']
            duration = self.duration_gen(
                data['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['text']['simpleText'])
            if not (title and thumbnails and hit_counts and doc_id):
                continue
            if duration > raw['duration_limit']:
                self.logger.warning('seconds > %ss' % raw['duration_limit'])
                continue
            source_url = 'https://www.youtube.com/watch?v=%s' % doc_id
            raw['title'] = title

            raw['thumbnails'] = [thumbnails]
            raw['hit_counts'] = hit_counts
            raw['doc_id'] = doc_id
            raw['duration'] = duration
            raw['source_url'] = source_url
            self.content_list.append(copy.deepcopy(raw))
            self.logger.warning(title)
            # break

        self.browse_times += 1
        if self.browse_times >= self.browse_limit:
            self.logger.info('browse_times is %s ' % self.browse_times)
            return

        browse_url = 'https://www.youtube.com/browse_ajax?ctoken=%s&itct=%s' % (ctoken, itct)
        self.logger.warning(browse_url)
        hd = {
            # 'cookie': 'VISITOR_INFO1_LIVE=jrLlcFZyJd0; YSC=3Qf7FrlhMOE; PREF=f1=50000000&f4=4000000&cvdm=grid&hl=en',
            'x-spf-previous': self.response_url,
            'x-spf-referer': self.response_url,
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20171018',
            'x-youtube-page-cl': '172568519',
            'x-youtube-page-label': 'youtube.ytfe.desktop_20171018_0_RC0',
            'x-youtube-variants-checksum': 'cc5602af9e6709df9857fcf09938a6dc',
        }
        yield Request(
            browse_url,
            headers=hd,
            meta=raw,
            dont_filter=True,
            callback=self.parse_browse
        )

    def parse_page(self, response):
        # print response.url
        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = dict()
        raw.update(response.meta)
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
        display_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="interactionCount"]/@content'

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
        raw['display_count'] = int(tree.xpath(display_selector)[0].replace(',', ''))

        raw['share_count'] = -1
        raw['comment_count'] = -1
        raw['like_count'] = 0
        raw['dislike_count'] = 0
        # 正则获取播放时间
        m_value, s_value = \
            re.findall('PT([0-9]+)M([0-9]+)S', tree.xpath(duration_raw_selector)[0])[0]
        # second_value = re.findall('<meta itemprop="duration" content="PT[0-9]+M([0-9]+)S">', body_instance)[0]
        raw['duration'] = int(m_value) * 60 + int(s_value)
        # if raw['duration'] > self.max_duration:
        #     print('duration > %d' % self.max_duration)
        #     return
        try:

            raw['like_count'] = int(
                tree.xpath('//*[@id="watch8-sentiment-actions"]/span/span[1]/button/span/text()')[0].replace(',', ''))
            raw['dislike_count'] = int(
                tree.xpath('//*[@id="watch8-sentiment-actions"]/span/span[3]/button/span/text()')[0].replace(',', ''))

            if self.locale == LOCALE_USA_ENGLISH:
                comments = YoutubeCommentUtil()
                doc_id = comments.fetch_comments(raw['source_url'])
                self.logger.info('doc_id %s : comments fetched' % doc_id)

            video_id = response.url.split('v=')[-1]
            static_html = YoutubeStatistic.fetch_statistic_page(video_id=video_id)
            tjson = json.loads(YoutubeStatistic.extract_statistics(static_html.encode('utf8')))[0]
            raw['share_count'] = tjson['shares']['cumulative']['opt']['vAxis']['maxValue']
            raw['share_peak'] = tjson['shares']['daily']['opt']['vAxis']['maxValue']
            # raw['share_array'] = tjson['shares']['daily']['data']

            raw['view_count'] = tjson['views']['cumulative']['opt']['vAxis']['maxValue']
            raw['view_peak'] = tjson['views']['daily']['opt']['vAxis']['maxValue']
            # raw['view_array'] = tjson['views']['daily']['data']

            raw['subscriber_count'] = tjson['subscribers']['cumulative']['opt']['vAxis']['maxValue']
            raw['subscriber_peak'] = tjson['subscribers']['daily']['opt']['vAxis']['maxValue']
            raw['subscriber_array'] = tjson['subscribers']['daily']['data']
            watch_time_str = re.findall("<span class=\"menu-metric-value\">(.*?)</span>", static_html)[0]
            raw['watch_time_arg'] = int(watch_time_str.split(":")[0]) * 60 + int(watch_time_str.split(":")[1])
            raw['comment_count'] = int(YoutubeStatistic.get_comments_count(video_id))

            raw['extra']['view_peak'] = raw['view_peak']
            raw['extra']['share_peak'] = raw['share_peak']
            raw['extra']['subscriber_peak'] = raw['subscriber_peak']
            raw['extra']['subscriber_count'] = raw['subscriber_count']
            raw['extra']['watch_time_arg'] = raw['watch_time_arg']
            raw['extra']['dislike_count'] = raw['dislike_count']



        except Exception, e:
            pass

        yield Request(
            raw['source_url'],
            headers=self.hd_page,
            meta=raw,
            dont_filter=True,
            callback=self.parse_video_from_other
        )

    def parse_video_from_other(self, response):
        target_url = "https://www.findyoutube.net/result"

        self.logger.warning('old parse_video_from_other function!!!!')

        post_dict = {
            "url": response.url,
            "submit": "Download"
        }

        ta = ['23.95.140.220:13228', '23.95.140.193:13228', '23.95.140.162:13228', '23.95.140.119:13228',
              '23.95.140.111:13228', '23.95.140.22:13228', '23.95.139.115:13228', '23.95.139.93:13228',
              '23.95.139.70:13228', '23.95.140.11:13228', '23.95.140.96:13228', '23.95.139.19:13228',
              '198.23.195.16:13228', '192.210.248.207:13228', '192.210.248.100:13228', '192.210.248.86:13228',
              '192.210.248.18:13228', '192.210.248.120:13228', '192.210.248.73:13228', '192.210.248.62:13228',
              '198.23.195.104:13228', '198.23.195.47:13228',
              '198.23.195.163:13228', '192.210.248.247:13228', '198.23.195.58:13228', ]
        tp = random.choice(ta)
        proxies = {
            'http': 'http://{}'.format(tp),
            'https': 'http://{}'.format(tp)
        }

        r = requests.post(target_url, proxies=proxies, data=post_dict)

        body_instance = r.content.replace('amp;', '')
        tree = lxml.html.fromstring(body_instance)

        # video_selector = '/html/body/div[2]/div/div[1]/table/tbody/tr[3]/td[3]/button/a/@href'

        tr_containers = tree.xpath('//*[@id="videos_modal"]/div/div/div[2]/table/tbody/tr')

        source_format_dict = dict()

        for each in tr_containers:
            temp_str = each.xpath('td[1]/text()')[0].strip()
            source_format_dict[temp_str] = each.xpath('td[3]/a/@href')[0]

        raw = dict()
        raw.update(response.meta)

        try:
            raw['video'], format_str = next(
                (v, k) for (k, v) in source_format_dict.iteritems() if '(medium) .mp4' in k)
            self.logger.warning("find target: " + format_str)
            raw['video_width'], raw['video_height'] = re.findall('(\d+)x(\d+)', format_str)[0]
            self.parse_raw(raw)
            return
        except Exception as e:
            traceback.print_exc()
            self.logger.error(e.message)
            pass

        try:
            raw['video'], format_str = next(
                (v, k) for (k, v) in source_format_dict.iteritems() if '(360p) .mp4' in k)
            self.logger.warning("find target: " + format_str)
            raw['video_width'], raw['video_height'] = re.findall('(\d+)x(\d+)', format_str)[0]
            self.parse_raw(raw)
            return
        except Exception as e:
            traceback.print_exc()
            self.logger.error(e.message)
            pass

        try:
            raw['video'], format_str = next(
                (v, k) for (k, v) in source_format_dict.iteritems() if '(480p) .mp4' in k)
            self.logger.warning("find target: " + format_str)
            raw['video_width'], raw['video_height'] = re.findall('(\d+)x(\d+)', format_str)[0]
            self.parse_raw(raw)
            return
        except Exception as e:
            traceback.print_exc()
            self.logger.error(e.message)
            pass

        try:
            raw['video'], format_str = next(
                (v, k) for (k, v) in source_format_dict.iteritems() if '(small) .mp4' in k)
            self.logger.warning("find target: " + format_str)
            raw['video_width'], raw['video_height'] = re.findall('(\d+)x(\d+)', format_str)[0]
            self.parse_raw(raw)
            return
        except Exception as e:
            traceback.print_exc()
            self.logger.error(e.message)
            pass

        self.record_invalid_source_url(raw['source_url'], 'findyoutube error')

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

        yield self.parse_raw(raw)

    def generate_message(self, article_info):
        message = super(YoutubeSpiderBase, self).generate_message(article_info)
        if message:
            if 'inlinks' in article_info['raw']:
                message['inlinks'] = article_info['raw']['inlinks']
            return message

    def duration_gen(self, sb):
        try:
            minute, second = sb.split(":")
            return float(int(minute) * 60 + int(second))
        except:
            return 100000000

    def get_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_html_from_raw(self, raw):
        return ''

    def get_raw_tags_from_raw(self, raw):
        tag_list = raw['tags']
        tag_list.insert(0, u'触宝_视频')
        return tag_list

    def title_duplicate(self, ttl):
        return False

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
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_keywords_from_raw(self, raw):
        return []

    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_source_name_from_raw(self, raw):
        return 'youtube'

    def get_video_id_count_from_raw(self, raw):
        return hashlib.md5(raw['video_id']).hexdigest()

    def get_video_height_from_raw(self, raw):
        return raw['video_height']

    def get_video_width_from_raw(self, raw):
        return raw['video_width']

    # 这里不能动，有实际需求复写这个函数
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

    def get_video_type_from_raw(self, raw):
        return VIDEO_TYPE_SHORT_VIDEO

    def get_input_type_from_raw(self, raw):
        return self.input_type

    def get_like_count_from_raw(self, raw):
        return raw['like_count']

    def get_comment_count_from_raw(self, raw):
        return raw['comment_count']

    def get_share_count_from_raw(self, raw):
        return raw['share_count']

    def get_view_count_from_raw(self, raw):
        return raw['display_count']
