# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware


class DupeFilter(FilterMiddleware):

    def __init__(self, *a, **kw):
        super(DupeFilter, self).__init__(*a, **kw)
        self.dedupkey_look_table = self.settings['DEDUPKEY_LOOK_TABLE']

    def process(self, item):
        account = item['account']
        dedup_key = item['dedup_key']
        longest_text = item['longest_text']
        old_score = self.redis_cli.hget(self.dedupkey_look_table, dedup_key)
        if not old_score or account.startswith('9'):
            return True
        is_winner = item['score'] >= int(old_score)
        if not is_winner:
            self.filter_standard_log(account,
                                     '(score: %d) loss, dedupkey: %s, longest_text: %s, old score: %d' %
                                     (item['score'], dedup_key, longest_text, int(old_score)))
        else:
            self.filter_standard_log(account,
                                     'dedupkey: %s, is_winner, old_score: %d, new_score: %d' %
                                     (dedup_key, int(old_score), item['score']))
        return is_winner
