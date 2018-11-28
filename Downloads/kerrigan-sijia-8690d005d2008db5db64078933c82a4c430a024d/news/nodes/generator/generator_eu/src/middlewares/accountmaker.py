# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class AccountMaker(MapMiddleware):

    def process(self, item):
        item['account'] = item['raw']['account']
        return item
