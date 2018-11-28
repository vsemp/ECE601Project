# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class ContentTypeMaker(MapMiddleware):
    def process(self, item):
        if 'content_type' in item['raw'] and item['raw']['content_type']:
            item['content_type'] = item['raw']['content_type']
        else:
            item['content_type'] = "default"
        return item
