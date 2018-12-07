# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware


class PageTypeFilter(FilterMiddleware):
    def process(self, item):
        account = item['account']
        page_type = item['page_type']
        if not page_type:
            self.filter_standard_log(item, account)
            return False
        return True
