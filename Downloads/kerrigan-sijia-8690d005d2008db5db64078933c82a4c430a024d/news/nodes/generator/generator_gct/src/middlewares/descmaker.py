# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware

class DescMaker(MapMiddleware):

    def process(self, item):
        desc = ''
        if 'desc' in item['raw'] and item['raw']['desc']:
            desc = item['raw']['desc']
        item['desc'] = desc
        return item
