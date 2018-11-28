# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware


class NoneFilter(FilterMiddleware):
    def __init__(self, *a, **kw):
        super(NoneFilter, self).__init__(*a, **kw)

    def process(self, item):
        if not item or not "raw" in item:
            self.logger.error("Item is None!!!!!!")
            return False
        return True
