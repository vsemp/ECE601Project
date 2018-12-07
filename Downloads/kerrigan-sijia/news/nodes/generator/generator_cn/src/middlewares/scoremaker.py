# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time
import sys


class ScoreMaker(MapMiddleware):

    def __init__(self, *a, **kw):
        super(ScoreMaker, self).__init__(*a, **kw)
        self.interest_weight = {
            'target_news': 20000,
            'top_news': 10000,
            'album_img_url': 10,
            'large_img_url': 5,
            'small_img_url': 3,
        }

    def process(self, item):
        item['score'] = self.score(item)
        if item['account'].startswith('9'):
            item['score'] = sys.maxint
        return item

    def score(self, item):
        pubts = int(time.mktime(time.strptime(item['time'], '%Y-%m-%d %X')))
        score = 0
        for interest in self.interest_weight:
            value = item.get(interest)
            weight = self.interest_weight[interest]
            if value:
                if isinstance(value, list):
                    score += len(value) * weight
                else:
                    score += weight
        score = (1 + score) * pubts
        return score
