# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class LoggerMaker(MapMiddleware):
    def process(self, item):
        item['crawl_id'] = item['raw'].get('crawl_id', [])
        return item
