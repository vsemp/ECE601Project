# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time


class CrawlTimeMaker(MapMiddleware):

    def process(self, item):
        crawl_time = item['raw']['crawl_time']
        crawl_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(crawl_time))
        item['crawl_time'] = crawl_time
        return item
