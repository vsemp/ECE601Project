# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class JumperMaker(MapMiddleware):

    def process(self, item):
        item['is_jump2src'] = item['raw'].get('is_jump2src', False)
        return item
