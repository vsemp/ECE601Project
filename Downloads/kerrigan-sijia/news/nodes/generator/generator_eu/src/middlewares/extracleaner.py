# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import json


class ExtraCleaner(MapMiddleware):

    def process(self, item):
        item.pop('raw')
        item = json.dumps(item,
                          ensure_ascii=False,
                          encoding='utf8',
                          sort_keys=True).encode('utf8')
        return item
