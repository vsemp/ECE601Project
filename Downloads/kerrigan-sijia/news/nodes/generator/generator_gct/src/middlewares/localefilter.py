# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware


class LocaleFilter(FilterMiddleware):
    def __init__(self, *a, **kw):
        super(LocaleFilter, self).__init__(*a, **kw)

    def process(self, item):
        if "locale" not in item:
            self.logger.error("Locale is None!!!!!!")
            return False
        if "region" not in item:
            self.logger.error("Region is None!!!!!!")
            return False
        return True
