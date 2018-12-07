# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time


class TimeMaker(MapMiddleware):

    def process(self, item):
        pubtime = item['raw']['time']
        item['time'] = pubtime
        pubdate = time.strftime('%Y-%m-%d', time.strptime(pubtime, '%Y-%m-%d %X'))
        item['pubdate'] = pubdate
        return item
