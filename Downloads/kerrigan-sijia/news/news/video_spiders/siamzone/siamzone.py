
import copy
import json
import lxml
import random
import re
import traceback

import requests
from pydispatch import dispatcher
import logging
from scrapy import signals, Request, Selector
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider





class siamzone(BaseSpider):
    name = 'siamzone'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    channel_list = [

        {'url': 'https://www.siamzone.com/clip/tag/%E0%B8%A0%E0%B8%B2%E0%B8%9E%E0%B8%A2%E0%B8%99%E0%B8%95%E0%B8%A3%E0%B9%8C',
         'tags': ['movie']},
        {'url': 'https://www.siamzone.com/clip/tag/%E0%B8%A5%E0%B8%B0%E0%B8%84%E0%B8%A3', 'tags': ['drama']},
        {'url': 'https://www.siamzone.com/clip/tag/%E0%B9%80%E0%B8%9E%E0%B8%A5%E0%B8%87%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B8%94%E0%B8%B2%E0%B8%A3%E0%B8%B2',
        'tags': ['Music and Celebrities']}

    ]

    content_list = []
    result = []
    browse_times = 0
    browse_limit = 2

    """
    def __init__(self, *a, **kw):
        super(siamzone, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop(0)
            self.logger.warning('content_list p'
                                'op ed')
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
    """
    def start_requests(self):
        cur = self.channel_list.pop(0)
        channel_url = cur['url']
        raw = dict()
        raw['tags'] = cur['tags']
        raw['inlinks'] = [channel_url]

        yield Request(
            #channel_url,
            'https://www.siamzone.com/clip/5121',
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_page
        )

    def parse_list(self, response):
        self.browse_times += 1
        sel = Selector(response)
        raw = dict()
        raw.update(response.meta)
        for i in sel.xpath('//ul[@class="uk-grid uk-grid-width-1-2 uk-grid-width-large-1-4 uk-grid-small"]//li'):
            raw['source_url'] = i.xpath('.//a//@href').extract()[0]
            self.content_list.append(copy.deepcopy(raw))
        if self.browse_times < self.browse_limit:
            next_page=sel.xpath('//ul[@class="uk-pagination uk-pagination-right"]//li//a//@href').extract()
            if(len(next_page)>0):
                next_page = 'https://www.siamzone.com/clip/'+next_page[-1]
            yield Request(
                next_page,
                meta=raw,
                headers=self.hd_page,
                dont_filter=True,
                callback=self.parse_list
            )

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        sel = Selector(response)
        raw['title'] = re.findall('<meta property="og:title" content="(.*?)" >', response.body)[0]
        raw['created time'] = re.findall('<meta http-equiv="last-modified" content="(.*?)" />', response.body)[0]
        raw['thumbnail'] = re.findall('<meta property="og:image" content="(.*?)">', response.body)[0]
        raw['video_width'] = re.findall('<meta property="og:video:width" content="(.*?)" />', response.body)[0]
        raw['video_height'] = re.findall('<meta property="og:video:height" content="(.*?)" />',response.body)[0]
        video_url = re.findall('<meta property="og:video" content="(.*?)">',response.body)[0]
        video_url = video_url.replace("https://www.youtube.com/v/","https://www.youtube.com/watch?v=")


        print (video_url)

        yield Request(
            video_url,
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_time

        )

    def parse_time(self,response):
        print (response.url)
        sel = Selector(response)
        raw = dict()
        raw.update(response.meta)
        time = sel.xpath('//div[@class="ytp-bound-time-right"]//text()').extract()[0]
        print (time)
        minute = int(time.split(":")[0])
        second = int(time.split(":")[1])
        duration = minute * 60 + second

        if duration<=120:
            raw['duration'] = duration
            yield Request(
               response.url,
                meta=raw,
                headers=self.hd_page,
                dont_filter=True,
                callback=self.parse_video_from_other

            )
        print (raw)

    def parse_video_from_other(self, response):
        pass
        target_url = "https://www.findyoutube.net/result"

        self.logger.warning('old parse_video_from_other function!!!!')
        print (response.url)
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

        r = requests.post(target_url, data=post_dict)

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
        print (raw)
        self.record_invalid_source_url(raw['source_url'], 'findyoutube error')

    def parse_raw(self, raw):
        logging.warning('parse_raw!!!')
        self.spider_logger.info(source_url=self.get_source_url_from_raw(raw), custom_info='source crawl finished')
        article_info = self.generate_article_info(raw)
        if article_info is None:
            logging.warning('article_info is None!!!')
            return
        account = article_info['account']
        message = self.generate_message(article_info)
        if message is None:
            self.spider_logger.error(source_url=article_info['source_url'], custom_info='generate_message failed')
            logging.error('Message is None: %s' % account)
            return
        else:
            self.send_msg(message)

    def record_invalid_source_url(self, source_url, invalid_info):
        doc_id = self.get_doc_id_from_source_url(source_url)
        record = dict()
        record['_id'] = doc_id
        record['source_url'] = source_url
        record['invalid_info'] = invalid_info
        self.logger.warning("record_invalid_source_url %s:%s" % (source_url, invalid_info))
        self.mongo_invalid_url_collection.replace_one({'_id': record['_id']}, record, True)

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(siamzone)
process.start()
