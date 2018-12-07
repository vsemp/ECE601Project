# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class ProcessModeMaker(MapMiddleware):

    def process(self, item):
        item['process_mode'] = item['raw'].get('process_mode','normal_mode')
        return item
