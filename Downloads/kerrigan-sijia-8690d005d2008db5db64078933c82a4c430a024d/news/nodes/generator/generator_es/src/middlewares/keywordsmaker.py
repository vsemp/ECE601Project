# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class KeywordsMaker(MapMiddleware):

    def process(self, item):
        item['keywords'] = list(set(item['raw']['keywords']))
        return item
