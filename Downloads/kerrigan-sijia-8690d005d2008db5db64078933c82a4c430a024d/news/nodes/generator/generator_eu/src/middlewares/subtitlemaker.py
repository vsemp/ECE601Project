# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class SubTitleMaker(MapMiddleware):

    def process(self, item):
        subtitle = item['raw']['subtitle']
        if len(subtitle) > 10:
            if item['account'].startswith('1'):
                subtitle = u'微信公众号'
            elif item['account'].startswith('3'):
                subtitle = u'今日头条号'
        item['subtitle'] = subtitle
        return item
