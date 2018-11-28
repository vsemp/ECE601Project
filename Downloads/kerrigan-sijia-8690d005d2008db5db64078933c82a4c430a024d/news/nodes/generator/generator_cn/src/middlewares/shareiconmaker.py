# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class ShareIconMaker(MapMiddleware):

    def process(self, item):
        share_icon = self.select_share_icon(item)
        item['share_icon'] = share_icon
        return item

    def select_share_icon(self, item):
        share_icon = ''
        if item.get('album_img_url'):
            share_icon = item['album_img_url'][0]
        if item['small_img_url']:
            share_icon = item['small_img_url']
        if item['large_img_url']:
            share_icon = item['large_img_url']
        if share_icon:
            return ''.join(share_icon.split('@')[0:-1]) + '@200w_200h'
        return self.settings['DEFAULT_SHARE_ICON']
