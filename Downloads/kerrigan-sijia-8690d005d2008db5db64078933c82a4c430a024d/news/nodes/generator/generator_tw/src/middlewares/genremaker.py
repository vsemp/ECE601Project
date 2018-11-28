# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class GenreMaker(MapMiddleware):

    def process(self, item):
        item['genre'] = item['raw'].get('genre', [])
        return item
