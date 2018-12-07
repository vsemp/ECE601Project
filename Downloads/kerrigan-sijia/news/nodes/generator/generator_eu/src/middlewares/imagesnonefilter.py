# /usr/bin/env python
# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware

class ImagesNoneFilter(FilterMiddleware):
    def process(self, item):
        account = item['account']
        if str(account).startswith("9"):
            return True
        if item['large_img_url'] != '' or item['small_img_url'] != '' or 'album_img_url' in item:
            return True
        self.filter_standard_log(account)
        return False
