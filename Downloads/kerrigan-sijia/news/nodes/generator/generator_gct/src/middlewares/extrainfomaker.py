# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class ExtraInfoMaker(MapMiddleware):
    def process(self, item):
        if 'extra' in item['raw'] and item['raw']['extra']:
            item['extra'] = item['raw']['extra']

        if 'comment_count' in item['raw'] and item['raw']['comment_count']:
            item['comment_count'] = item['raw']['comment_count']

        if 'like_count' in item['raw'] and item['raw']['like_count']:
            item['like_count'] = item['raw']['like_count']

        if 'article_class' in item['raw'] and item['raw']['article_class']:
            item['article_class'] = item['raw']['article_class']

        if 'view_count' in item['raw'] and item['raw']['view_count']:
            item['view_count'] = item['raw']['view_count']

        if 'recommend_count' in item['raw'] and item['raw']['recommend_count']:
            item['recommend_count'] = item['raw']['recommend_count']

        if 'share_count' in item['raw'] and item['raw']['share_count']:
            item['share_count'] = item['raw']['share_count']

        if 'inlinks' in item['raw'] and item['raw']['inlinks']:
            item['inlinks'] = item['raw']['inlinks']
        else:
            item['inlinks'] = []

        if 'source_url_id' in item['raw']:
            item['source_url_id'] = item['raw']['source_url_id']

        return item
