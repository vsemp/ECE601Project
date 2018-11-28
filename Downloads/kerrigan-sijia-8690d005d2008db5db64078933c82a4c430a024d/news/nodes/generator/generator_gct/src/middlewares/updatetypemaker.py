# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import hashlib


class UpdatetypeMaker(MapMiddleware):
    def __init__(self, *a, **kw):
        super(UpdatetypeMaker, self).__init__(*a, **kw)
        self.account_look_table = self.settings['ACCOUNT_LOOK_TABLE']
        self.target_table = self.settings['TARGET_NEWS']
        self.fp_interests = [
            # 'content'
        ]

    def _fingerprint(self, item):
        fp_str = u''
        for key in self.fp_interests:
            fp_str += item.get(key, u'')
        fp_str = fp_str.encode('utf8')
        fp = hashlib.md5(fp_str).hexdigest()
        return fp

    def process(self, item):
        account = item['account']
        # old_fp = self.redis_cli.hget(self.account_look_table, account)
        new_fp = self._fingerprint(item)
        # if old_fp:
        #     item['need_upload'] = False
        #     if new_fp == old_fp:
        #         item['update_type'] = 0 if account.startswith('9') and not \
        #                             self.redis_cli.hget(self.target_table, account) else 1
        #     else:
        #         item['update_type'] = 1
        # else:
        #     item['update_type'] = 0 if account.startswith('9') and not \
        #                             self.redis_cli.hget(self.target_table, account) else 1
        #     item['need_upload'] = True
        item['need_upload'] = True
        if item['process_mode'] == 'update_mode':
            item['need_upload'] = True

        if item['process_mode'] == 'sim_mode':
            item['need_upload'] = True

        item['fingerprint'] = new_fp
        return item
