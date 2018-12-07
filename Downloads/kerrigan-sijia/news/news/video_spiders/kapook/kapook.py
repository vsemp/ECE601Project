import copy
import json
import re
import requests
from pydispatch import dispatcher
from scrapy import signals, Request, Selector
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider

class kapook(BaseSpider):
    name = 'mathai'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    category_list = [

        {'url': 'https://world.kapook.com/clip/food', 'tag': 'food'},
        {'url': 'https://world.kapook.com/clip/star', 'tag': 'star'}
    ]
    content_list = []
    result = []
    browse_times = 0
    browse_limit = 2

    def __init__(self, *a, **kw):
        super(kapook, self).__init__(*a, **kw)
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

        elif self.category_list:
            self.browse_times = 0
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)


    def parse_list(self,response):
        raw = dict()
        raw.update(response.meta)
        sel = Selector(response)
