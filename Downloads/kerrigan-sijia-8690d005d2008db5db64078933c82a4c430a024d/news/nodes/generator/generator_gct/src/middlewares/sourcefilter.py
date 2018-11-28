# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware


class SourceFilter(FilterMiddleware):

    def process(self, item):
        return True
