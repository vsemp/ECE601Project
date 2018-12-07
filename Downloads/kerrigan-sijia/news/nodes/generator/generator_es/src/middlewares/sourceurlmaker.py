# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class SourceUrlMaker(MapMiddleware):
    def process(self, item):
        item['source_url'] = item['raw']['url']['source_url']
        # if item['raw']['source_url_id']:
        item['source_url_id'] = item['raw'].get('source_url_id', 'error')
        return item
