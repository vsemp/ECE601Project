# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class SourceUrlMaker(MapMiddleware):

    def process(self, item):
        item['source_url'] = item['raw']['url']['source_url']
        return item
