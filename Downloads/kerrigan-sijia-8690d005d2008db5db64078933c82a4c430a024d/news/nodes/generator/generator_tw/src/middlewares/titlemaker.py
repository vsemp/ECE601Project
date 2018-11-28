# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import re


class TitleMaker(MapMiddleware):

    disallowed_words = [
        u'GIF',
        u'图',
    ]
    disallowed_prefix = [
        u'GIF-'
    ]
    replace_rules = {
        u'\\t': ' ',
        u'\\"': '"',
        u'✔': '',
        u'✅': '',
    }

    def process(self, item):
        title = item['raw']['title'].replace('\r', '').replace('\n', '').strip()
        title = self._process(title)
        item['title'] = title
        return item

    def _process(self, title):
        title = title.replace(u'（', u'(').replace(u'）', u')')
        title = re.sub(r'\s+', ' ', title)
        m = re.findall(u'(\([^\)]*\))', title)
        for word in m:
            if not word.strip(u'()'):
                title = title.replace(word, '')
                continue
            word_upper = word.upper()
            for disallowed_word in self.disallowed_words:
                if disallowed_word in word_upper:
                    title = title.replace(word, '')
        title_upper = title.upper()
        for prefix in self.disallowed_prefix:
            if title_upper.startswith(prefix):
                title = title[len(prefix):]
                break
        for rule in self.replace_rules:
            title = title.replace(rule, self.replace_rules[rule])
        return title
