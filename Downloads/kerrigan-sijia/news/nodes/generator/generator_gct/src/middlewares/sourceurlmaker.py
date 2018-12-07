# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class SourceUrlMaker(MapMiddleware):
    def process(self, item):
        item['source_url'] = item['raw']['url']['source_url']
        item['source_name'] = item['raw']['source_name']
        item['source_id'] = item['raw']['account'].split('-')[0]
        return item
