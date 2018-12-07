# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import json
import os


class SimMode(MapMiddleware):
    def process(self, item):
        if item['process_mode'] != 'sim_mode':
            return item
        item['target_url'] = str(item['target_url']).replace('news/', 'news/sim_mode/')
        item['large_img_url'] = str(item['large_img_url']).replace('news/', 'news/sim_mode/')
        item['share_icon'] = str(item['share_icon']).replace('news/', 'news/sim_mode/')
        item['small_img_url'] = str(item['small_img_url']).replace('news/', 'news/sim_mode/')
        if "publisher_icon_url" in item:
            item['publisher_icon_url'] = str(item['publisher_icon_url']).replace('news/', 'news/sim_mode/')

        item['recall'] = str(item['recall']).replace('com/news/', 'com/news/sim_mode/')
        item['dedup_key'] = str(item['dedup_key']) + '_sim'

        return item
