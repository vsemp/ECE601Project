# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import json


class TargetNewsMaker(MapMiddleware):

    def process(self, item):
        account = item['account']
        target_info = self.redis_cli.hget(
            self.settings['TARGET_NEWS'],
            account)
        if target_info is not None:
            target_info = json.loads(target_info)
            target_setting = {}
            target_setting['type'] = target_info['type']
            target_setting['valid_time'] = target_info['valid_time']
            target_setting['news_index'] = target_info['news_index']
            target_setting['push_type'] = target_info.get('push_type', 'push_type_normal')
            target_setting['push_range'] = target_info.get('push_range', -1)
            target_setting['push_group'] = target_info.get('push_group', '')
            target_setting['push_os'] = target_info.get('push_os', 'android_ios')
            target_setting['push_personal'] = target_info.get('push_personal')
            item['target_news'] = target_setting
            self.logger.info('Account %s' % account)
        return item
