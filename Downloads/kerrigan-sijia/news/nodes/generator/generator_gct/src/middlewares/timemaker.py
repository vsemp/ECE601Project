# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time


class TimeMaker(MapMiddleware):
    def process(self, item):
        pubtime = item['raw']['publish_time']
        item['publish_time'] = pubtime
        item['publish_ts'] = long(time.mktime(time.strptime(pubtime, '%Y-%m-%d %X')))
        pubdate = time.strftime('%Y-%m-%d',time.localtime())
        item['pubdate'] = pubdate
        return item
