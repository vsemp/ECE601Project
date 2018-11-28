# /usr/bin/env python
# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import hashlib


class DedupTitleFilter(FilterMiddleware):
    def process(self, item):
        if u'触宝_美图' in item['raw']['raw_tags']:
            return True
        else:
            account = item['raw']['account']
            if str(account).startswith("9"):
                return True
            else:
                title_md5 = hashlib.md5(item['raw']['title'].encode("utf-8")).hexdigest()
                if self.title_duplicate(title_md5):
                    self.filter_standard_log(account)
                    return False
                else:
                    return True

    def title_duplicate(self, title_md5):
        return bool(self.redis_cli.hget(self.title_look_table, title_md5))
