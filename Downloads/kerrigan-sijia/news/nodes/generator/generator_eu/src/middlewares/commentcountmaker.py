# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class CommentCountMaker(MapMiddleware):

    DEFAULT_COMMENTCOUNT = 0

    def process(self, item):
        item['comment_count'] = item['raw'].get('comment_count', self.DEFAULT_COMMENTCOUNT)
        return item
