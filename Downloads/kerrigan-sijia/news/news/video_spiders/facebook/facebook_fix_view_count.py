from facebook_base import FacebookSpiderBase
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
import pymongo


class FacebookSpider(FacebookSpiderBase):
    name = 'facebook_fix_view_count'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL
    duration_limit = 60 * 60
    # conn = MongoClient(
    #     'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
    #     readPreference="primary")
    conn = MongoClient(
        'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
        readPreference="primary")

    # conn = MongoClient("localhost:27017")
    db = conn.news
    my_set = db.documents

    content_list = []

    def __init__(self, *a, **kw):
        super(FacebookSpiderBase, self).__init__(*a, **kw)
        for i in self.my_set.find({"$and": [{"source_name": "facebook"}, {"view_count": -1}]}):

            hash_value = settings.getint("hash_value", default=-1)
            hash_total = settings.getint("hash_total", default=-1)

            source_hash = int(hashlib.md5(str(i['source_url'])).hexdigest(), 16)
            if hash_value != -1 and hash_total != -1:
                if source_hash % hash_total != hash_value:
                    continue
                else:
                    pass
                    # self.logger.warning("hash pick!")
            self.content_list.append(i['source_url'])
        self.logger.info("content_list len is %s" % len(self.content_list))
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        source_url = self.content_list.pop(0)
        raw = dict()
        raw['source_url'] = source_url
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

        try:
            raw['view_count'] = int(re.findall('viewCount:"([0-9,]+)"', body_instance)[0].replace(',', ''))
            raw['like_count'] = int(re.findall('likecount:([0-9,]+)', body_instance)[0].replace(',', ''))
            raw['comment_count'] = int(re.findall('commentcount:([0-9,]+)', body_instance)[0].replace(',', ''))
            raw['share_count'] = int(re.findall('sharecount:([0-9,]+)', body_instance)[0].replace(',', ''))

        except Exception, e:
            pass

        self.my_set.update({"source_url": raw['source_url']}, {'$set': {"view_count": raw['view_count']}}, multi=True)
        self.my_set.update({"source_url": raw['source_url']}, {'$set': {"comment_count": raw['comment_count']}},
                           multi=True)
        self.my_set.update({"source_url": raw['source_url']}, {'$set': {"like_count": raw['like_count']}}, multi=True)
        self.my_set.update({"source_url": raw['source_url']}, {'$set': {"share_count": raw['share_count']}}, multi=True)
        # self.my_set.update({"source_url": raw['source_url']}, {'$set': {"extra": raw['extra']}}, multi=True)
        self.logger.info("%s_updated,view_count is %s" % (raw['source_url'], raw['view_count']))
