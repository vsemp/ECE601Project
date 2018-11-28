# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class LocationMaker(MapMiddleware):

    def process(self, item):
        item['location'] = item['raw']['location']
        return item
