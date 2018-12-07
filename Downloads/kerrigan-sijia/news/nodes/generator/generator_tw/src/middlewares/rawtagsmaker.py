# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import json
import base64


class RawTagsMaker(MapMiddleware):

    def __init__(self, *a, **kw):
        super(RawTagsMaker, self).__init__(*a, **kw)
        self.replace_tags = {
            u'触宝_视频': u'视频',
        }

    def process(self, item):
        item['raw_tags'] = []
        raw = self.redis_news_cli.get(item['account'])
        if raw:
            news_info = json.loads(base64.b64decode(raw))
            item['raw_tags'].extend(news_info.get('raw_tags', []))
        for raw_tag in item['raw'].get('raw_tags', []):
            raw_tag = raw_tag.strip()
            if raw_tag in self.replace_tags:
                raw_tag = self.replace_tags[raw_tag]
            if raw_tag not in item['raw_tags']:
                item['raw_tags'].append(raw_tag)
        return item
