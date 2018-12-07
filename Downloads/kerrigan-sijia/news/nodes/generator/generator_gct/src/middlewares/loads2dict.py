# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import json


class Loads2Dict(MapMiddleware):

    def process(self, item):
        new_item = {}
        new_item['raw'] = json.loads(item)
        new_item['raw'].pop('html', None)
        return new_item
