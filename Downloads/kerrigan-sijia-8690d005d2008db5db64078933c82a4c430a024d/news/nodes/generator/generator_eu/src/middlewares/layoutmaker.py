# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class TargetLayoutMaker(MapMiddleware):

    def process(self, item):
        if item.get('target_news'):
            if item['large_img_url']:
                item['small_img_url'] = ''
                item.pop('album_img_url', None)
            elif item.get('album_img_url'):
                item['small_img_url'] = ''
        return item
