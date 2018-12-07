# -*- coding: utf-8 -*-
from src.middlewares.base import MapPartitionsMiddleware
from src.util.breaking_news_util import add_duration
import redis
import json


class BreakingNewsMaker(MapPartitionsMiddleware):

    def process(self, messages):
        item_list = []
        for item in messages:
            item['breaking_news'] = {}
            raw = self.redis_cli.hget(
                self.settings['BREAKING_NEWS_ACCOUNT_LOOK_TABLE'],
                item['account'])
            if raw:
                breaking_news_info = json.loads(raw)
                add_duration(item,
                             location_list=breaking_news_info['location'],
                             duration=breaking_news_info['duration'],
                             mode=breaking_news_info['mode'])
            if item['account'].startswith('9'):
                item['breaking_news'] = {}
            item_list.append(item)
        return item_list
