# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware


class TagsFilter(FilterMiddleware):

    def __init__(self, *a, **kw):
        super(TagsFilter, self).__init__(*a, **kw)
        self.bad_tags = [u'广告']

    def process(self, item):
        account = item['account']
        tags = [x[0] for x in item['tags']]
        for bad_tag in self.bad_tags:
            if bad_tag in tags:
                self.filter_standard_log(account)
                return False
        return True
