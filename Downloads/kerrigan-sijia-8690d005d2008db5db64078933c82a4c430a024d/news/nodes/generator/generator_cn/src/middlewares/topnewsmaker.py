# -*- coding: utf-8 -*-
from src.middlewares.base import MapPartitionsMiddleware
import json


class TopNewsMaker(MapPartitionsMiddleware):

    def __init__(self, *a, **kw):
        super(TopNewsMaker, self).__init__(*a, **kw)
        self.top_news_info = self.settings['TOP_NEWS_INFO']
        self.range = self.settings['TIME_RANGE']

    def process(self, messages):
        item_list = []
        for item in messages:
            try:
                news_info = json.loads(self.redis_cli.get(self.top_news_info))
            except TypeError:
                item_list.append(item)
                continue
            if item['account'] == news_info['account']:
                item['top_news'] = news_info['duration']
            item_list.append(item)
        return item_list
