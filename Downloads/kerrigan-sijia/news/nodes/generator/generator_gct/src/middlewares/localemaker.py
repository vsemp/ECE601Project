# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time


class LocaleMaker(MapMiddleware):
    def process(self, item):
        item['locale'] = item['raw'].get('locale', 'unknown')
        item['locales'] = item['raw'].get('locales', [])
        if not item['locales']:
            item['locales'].append(item['locale'])

        if 'region' in item['raw'] and item['raw']['region']:
            item['region'] = item['raw']['region']
        return item
