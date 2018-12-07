# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
from pkg_resources import resource_filename
import hashlib
import struct
import re


class DedupKeyMaker(MapMiddleware):
    invalid_text = []

    def __init__(self, *a, **kw):
        super(DedupKeyMaker, self).__init__(*a, **kw)
        for item in open(resource_filename('resources', 'invalid_text')).read().splitlines():
            self.invalid_text.append(item.decode('utf8'))

    def _str_com(self, x, y):
        if len(x) == len(y):
            if x < y:
                return -1
            elif x > y:
                return 1
            else:
                return 0
        else:
            return len(x) - len(y)

    def process(self, item):
        url = item['raw'].get('url', None)
        source_url = url.get('source_url', None) if url else None
        longest_text = source_url
        dedup_key = struct.unpack("<Q", hashlib.md5(longest_text.encode('utf8')).digest()[:8])[0]
        dedup_key = str(dedup_key)
        item['longest_text'] = longest_text
        item['dedup_key'] = dedup_key
        self.logger.info('longest_text %s' % longest_text)
        self.logger.info('dedup_key %s' % dedup_key)
        return item
