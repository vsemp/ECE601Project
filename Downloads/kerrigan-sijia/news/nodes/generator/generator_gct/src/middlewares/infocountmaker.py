# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class InfoCountMaker(MapMiddleware):

    DEFAULT_HITCOUNT = 0

    def process(self, item):
        item['hit_count'] = item['raw'].get('hit_count', self.DEFAULT_HITCOUNT)
        return item
