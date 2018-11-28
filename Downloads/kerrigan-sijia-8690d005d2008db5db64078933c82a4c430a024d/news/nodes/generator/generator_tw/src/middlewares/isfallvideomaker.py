# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time

class IsfallvideoMaker(MapMiddleware):

    def process(self, item):
        item['is_fall_video'] = item['raw'].get('is_fall_video', False)
        return item