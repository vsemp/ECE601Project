# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class VideoSizeMaker(MapMiddleware):

    def process(self, item):
        raw = item['raw']
        if raw.get('video_height') and raw.get('video_width'):
            item['video_height'] = raw['video_height']
            item['video_width'] = raw['video_width']
        return item
