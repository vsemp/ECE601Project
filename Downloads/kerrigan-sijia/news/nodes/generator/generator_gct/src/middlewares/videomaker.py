# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class VideoMaker(MapMiddleware):

    def process(self, item):
        raw = item['raw']
        if raw.get('video'):
            item['video'] = raw['video']
        return item
