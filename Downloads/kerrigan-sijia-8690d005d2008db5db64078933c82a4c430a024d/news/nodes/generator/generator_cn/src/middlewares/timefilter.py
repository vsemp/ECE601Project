# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import time


class TimeFilter(FilterMiddleware):

    def __init__(self, *a, **kw):
        super(TimeFilter, self).__init__(*a, **kw)
        self.range = self.settings['TIME_RANGE']
        self.video_range = self.settings['VIDEO_TIME_RANGE']

    def process(self, item):
        account = item['raw']['account']
        now = int(time.time())
        pubtime = item['raw']['time']
        pubtime = time.mktime(time.strptime(pubtime, '%Y-%m-%d %X'))
        time_range = self.video_range if item.get('video') else self.range
        if not account.startswith('9') and not self._is_time_correct(pubtime, now, time_range):
            err_info = 'time %s, is video = %s' % (item['raw']['time'], item.get('video') == True)
            self.filter_standard_log(account, err_info)
            return False
        return True

    def _is_time_correct(self, time_check, time_now, time_range):
        return time_now - time_range <= time_check and time_check <= time_now
