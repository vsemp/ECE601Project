# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import re


class ChineseFilter(FilterMiddleware):

    def process(self, item):
        if item.get('video'):
            return self.check_video(item)
        else:
            return self.check_non_video(item)

    def check_non_video(self, item):
        account = item['account']
        content = item['content']
        texts = re.findall(ur'[\u4e00-\u9fa5]+', content)
        if item.get('is_jump2src', False):
            return True

        if not texts:
            if item['account']:
                for content_part in item['raw']['content']:
                    if 'image' in content_part:
                        return True
            self.filter_standard_log(account)
            return False
        return True

    def check_video(self, item):
        account = item['account']
        title = item['title']
        texts = re.findall(ur'[\u4e00-\u9fa5]+', title)
        if not texts:
            self.filter_standard_log(account)
            return False
        return True
