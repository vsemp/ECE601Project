# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import time

class CommentMaker(MapMiddleware):

    def process(self, item):
        item['comment'] = []
        for comment in item['raw'].get('comment', []):
            if len(set(comment.keys()) & {u'ct', u'ts'}) != 2:
                continue
            try:
                ts = time.localtime(comment['ts'])
            except Exception, e:
                continue
            if not (isinstance(comment['ct'], unicode) or isinstance(comment['ct'], str)):
                continue
            item['comment'].append(comment)
        return item