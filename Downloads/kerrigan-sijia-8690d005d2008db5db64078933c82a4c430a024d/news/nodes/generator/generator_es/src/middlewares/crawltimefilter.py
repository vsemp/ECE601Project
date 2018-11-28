# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import logging


class CrawlTimeFilter(FilterMiddleware):
    def process(self, item):
        account = item['raw']['account']
        crawl_time = item['raw']['crawl_time']
        if not isinstance(crawl_time, (float, long, int)):
            self.filter_standard_log(item, account)
            return False
        return True
