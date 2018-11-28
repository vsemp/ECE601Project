# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import hashlib
import struct
import re


class DedupKeyMaker(MapMiddleware):

    invalid_text = []

    def __init__(self, *a, **kw):
        super(DedupKeyMaker, self).__init__(*a, **kw)
        for item in open(self.get_resource_file_path('invalid_text')).read().splitlines():
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
        longest_text = ''
        content = item['content']
        texts = re.findall(ur'[\u4e00-\u9fa5]+', content)
        if texts:
            texts.sort(self._str_com, reverse=True)
            longest_text = texts[0]
        if not longest_text or longest_text in self.invalid_text:
            m = re.findall(ur'[\u4e00-\u9fa5]+', item['raw']['title'])
            longest_text = ''.join(m)
        dedup_key = struct.unpack("<Q", hashlib.md5(longest_text.encode('utf8')).digest()[:8])[0]
        dedup_key = str(dedup_key)
        item['longest_text'] = longest_text
        item['dedup_key'] = dedup_key
        return item
