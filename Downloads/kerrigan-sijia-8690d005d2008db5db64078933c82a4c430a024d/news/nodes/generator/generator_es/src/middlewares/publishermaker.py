# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class PublisherMaker(MapMiddleware):
    def process(self, item):
        item['publisher'] = item['raw'].get('publisher', "")
        item['publisher_id'] = item['raw'].get('publisher_id', "")
        return item
