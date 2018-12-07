# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware

class PageTypeMaker(MapMiddleware):

    def process(self, item):
        page_type = ''
        if 'page_type' in item['raw'] and item['raw']['page_type']:
            page_type = item['raw']['page_type']
        else:
            tags = [x[0] for x in item['tags']]
            if u'图集' in tags:
                page_type = 'album'
            elif item['raw'].get('is_fall_video', False):
                page_type = 'fall_video'
            elif u'触宝_美图' in tags:
                page_type = 'album'
            elif u'视频' in tags:
                page_type = 'video'
            elif item['account'].startswith('231-'):
                page_type = 'tencent_open'
            else:
                page_type = 'article'
        #hard code page_type to tencent_open to using webview in Android
        #can remove if old version goes down
        if page_type == 'href_article' and item['account'].startswith('9'):
            page_type = 'tencent_open'
        item['page_type'] = page_type
        return item
