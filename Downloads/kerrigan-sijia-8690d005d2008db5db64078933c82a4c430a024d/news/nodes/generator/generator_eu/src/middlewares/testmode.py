# -*- coding: utf-8 -*-
from src.middlewares.base import MapPartitionsMiddleware
import json
import os


class TestMode(MapPartitionsMiddleware):

    def __init__(self, *a, **kw):
        super(TestMode, self).__init__(*a, **kw)
        self.test_dir = self.settings.get('TEST_DIR', '.')

    def process(self, messages):
        if not self.settings.get('TEST_MODE', False):
            return messages
        for item in messages:
            account = item['account']
            html = item['html']
            if html:
                open(os.path.join(self.test_dir, '%s.html' % account), 'w').write(html)
            self.logger.info(self.pretty_show(item))
        return messages

    def pretty_show(self, item):
        item_copy = item.copy()
        item_copy.pop('raw', None)
        item_copy.pop('html', None)
        item_copy.pop('content', None)
        return json.dumps(item_copy, ensure_ascii=False, encoding='utf8').encode('utf8')
