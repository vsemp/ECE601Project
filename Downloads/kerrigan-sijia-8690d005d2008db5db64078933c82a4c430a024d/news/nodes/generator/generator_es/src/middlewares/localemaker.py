# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time

class LocaleMaker(MapMiddleware):

    def process(self, item):
        item['locale'] = item['raw'].get('locale', 'unknown')
        return item