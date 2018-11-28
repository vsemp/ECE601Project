from youtube_base import YoutubeSpiderBase
from ...spider_const import *
from pymongo import MongoClient
from scrapy.conf import settings
import hashlib
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from pymongo import MongoClient
import json
import lxml
import re
from tools.statistic import YoutubeStatistic
import pymongo


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_fix_keywords'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL
    duration_limit = 60 * 60
    conn = MongoClient(
        'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
        readPreference="primary")
    # conn = 'localhost:27017'
    db = conn.news
    my_set = db.documents

    content_list = []

    def __init__(self, *a, **kw):
        super(YoutubeSpiderBase, self).__init__(*a, **kw)
        for i in self.my_set.find({"$and": [{"source_name": "youtube"}, {"keywords": []}]}):
            hash_value = settings.getint("hash_value", default=-1)
            hash_total = settings.getint("hash_total", default=-1)

            source_hash = int(hashlib.md5(str(i['source_url'])).hexdigest(), 16)
            if hash_value != -1 and hash_total != -1:
                if source_hash % hash_total != hash_value:
                    continue
                else:
                    pass
                    # self.logger.warning("hash pick!")
            self.content_list.append(i)
        self.logger.info("content_list len is %s" % len(self.content_list))
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        item = self.content_list.pop(0)
        raw = dict()
        print item['source_url']
        raw['_id'] = item['_id']
        raw['source_url'] = item['source_url']
        raw['raw_extra_info'] = item['extra']
        self.logger.info(raw['source_url'])
        yield Request(
            raw['source_url'],
            headers=self.hd_page,
            meta=raw,
            callback=self.parse_page
        )

    def parse_page(self, response):
        # print response.url
        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = dict()
        raw.update(response.meta)

        raw['extra_info'] = dict()
        if re.findall('<meta property="og:restrictions:age" content="(.*?)">', body_instance):
            raw['extra_info']['restriction_age'] = re.findall('<meta property="og:restrictions:age" content="(.*?)">',
                                                              body_instance)[0]

        for key in raw['raw_extra_info']:
            if key == 'key':
                continue
            raw['extra_info'][key] = raw['raw_extra_info'][key]

        raw['keywords'] = []
        if re.findall('"keywords":"(.*?)"', body_instance):
            for each in re.findall('"keywords":"(.*?)"', body_instance)[0].split(','):
                raw['keywords'].append(each.strip())
        elif re.findall('<meta name="keywords" content="(.*?)">', body_instance):
            for each in re.findall('<meta name="keywords" content="(.*?)">', body_instance)[0].split(','):
                raw['keywords'].append(each.strip())

        self.my_set.update({"_id": raw['_id']},
                           {'$set': {"extra": raw['extra_info'], "keywords": raw['keywords']}})
