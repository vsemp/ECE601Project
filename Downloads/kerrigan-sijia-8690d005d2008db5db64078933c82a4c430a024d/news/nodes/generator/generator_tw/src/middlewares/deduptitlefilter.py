# /usr/bin/env python
# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import hashlib


class DedupTitleFilter(FilterMiddleware):
    title_expiration_days = 14

    def process(self, item):
        if u'触宝_美图' in item['raw']['raw_tags']:
            return True
        elif 'video' in item['raw']:
            return True
        elif item['process_mode'] == 'update_mode':
            return True
        elif item['process_mode'] == 'sim_mode':
            return True
        else:
            if self.old_deduptitle_logic(item):
                return self.new_deduptitle_logic(item)
            else:
                return False

    def new_deduptitle_logic(self, item):
        account = item['raw']['account']
        if str(account).startswith("9"):
            return True
        else:
            title_md5 = hashlib.md5(item['raw']['title'].encode("utf-8")).hexdigest()
            if self.title_duplicate(title_md5):
                self.filter_standard_log(item, account)
                return False
            else:
                return True

    def title_duplicate(self, title_md5):
        return bool(self.redis_cli.hget(self.title_look_table, title_md5))

    def old_deduptitle_logic(self, item):
        account = item['raw']['account']
        if str(account).startswith("9"):
            return True
        else:
            title_md5 = hashlib.md5(item['raw']['title'].encode("utf-8")).hexdigest()
            flag_title_valid = True
            for i in range(self.title_expiration_days):
                if self.redis_cli.sismember("day" + str(i), title_md5) == 1:
                    flag_title_valid = False
                    break
            if not flag_title_valid:
                self.filter_standard_log(item, account)
            return flag_title_valid
