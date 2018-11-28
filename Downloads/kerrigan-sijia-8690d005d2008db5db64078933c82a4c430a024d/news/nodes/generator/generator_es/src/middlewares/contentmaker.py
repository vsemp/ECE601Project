# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import re


class ContentMaker(MapMiddleware):
    def __init__(self, *a, **kw):
        super(ContentMaker, self).__init__(*a, **kw)
        self.invalid_pattern = [
            re.compile(u'({([-_\s\w]*:[^;]*;)+})'),  # CSS codes
            re.compile(u'var\s+\w+'),  # JavaScript codes
            re.compile(u'((?i)</?[a-z][-:\.a-z0-9]*(?=[\s>])(\'[^\']*\'|"[^"]*"|[^\'">])*>)'),  # HTML tags
        ]
        self.bad_starts = [
            u'免责声明：',
            u'更多有态度内容请下载网易新闻',
            u'更多文章，长按关注',
            u'怎样才能不错过每天的新闻七点整',
        ]
        self.bad_words_of_last_line = [
            u'点击',
            u'滚动',
        ]
        self.sign_related = [
            u'相关新闻',
            u'更多阅读',
            u'往期推荐',
        ]
        self.meitu_ratio_floor_limit = float(9) / 16
        self.meitu_ratio_ceil_limit = float(16) / 9

    def process(self, item):
        if item['raw'].get('locale', 'unknown') in ['zh_TW']:
            return self.process_for_all(self.process_for_meitu(item))
        else:
            return self.process_for_ar_AR(item)

    def process_for_ar_AR(self, item):
        raw = item['raw']
        contents = []
        count_image = 0
        for element in raw['content']:
            text = element['text'] if 'text' in element else ''
            if 'image' not in element:
                if not text:
                    continue
            else:
                count_image += 1
            contents.append(element)
        raw['content'] = contents
        text_list = []
        for element in contents:
            text_list.append(element['text'])
        contents_text = ' '.join(text_list)
        normalized_content = ' '.join(contents_text.split())
        item['content'] = normalized_content
        item['count_image'] = count_image
        return item

    def process_for_all(self, item):
        raw = item['raw']
        contents = []
        word_ch = 0
        word = 0
        count_image = 0
        for element in raw['content']:
            text = element['text'] if 'text' in element else ''
            if not self.detect_invalid_pattern(text):
                contents = []
                break
            m = re.findall(ur'[\u4e00-\u9fa5]+', text)
            text_norm = ''.join(m)
            if text_norm in self.sign_related:
                # stop adding more elements, ie, filter subsequent elements
                break
            if 'image' not in element:
                if not text:
                    # filter this meaningless element
                    continue
            else:
                count_image += 1
            need_filter = False
            for bad_start in self.bad_starts:
                if text.startswith(bad_start):
                    need_filter = True
                    break
            if need_filter:
                continue
            contents.append(element)
            for character in text:
                if 0x4e00 <= ord(character) <= 0x9fa5:
                    word_ch += 1
            word += len(text)
        # check if English plays a dominant role in this article
        # articles with some English references will be misjudged
        if word and float(word_ch) / word < 0.5:
            if item['account'][0] not in {'1', '9'} or word <= 40 or not count_image:
                contents = []
        if contents:
            for bad_word in self.bad_words_of_last_line:
                if bad_word in contents[-1]['text'] and 'rich_content' not in item['raw']:
                    contents.pop()
                    break
        raw['content'] = contents
        text_list = []
        for element in contents:
            text_list.append(element['text'])
        contents_text = ' '.join(text_list)
        normalized_content = ' '.join(contents_text.split())
        item['content'] = normalized_content
        item['count_image'] = count_image
        return item

    def detect_invalid_pattern(self, text):
        for invalid_pattern in self.invalid_pattern:
            m = invalid_pattern.search(text)
            if m:
                return False
        return True

    def process_for_meitu(self, item):
        if u'触宝_美图' in item['raw']['raw_tags']:
            item['raw']['content'] = filter(self.filter_by_ratio, item['raw']['content'])
        return item

    '''
    images in content that do not meet the requirement of ratio will be filtered
    if all images were filtered, that meitu will be droped
    '''

    def filter_by_ratio(self, ele):
        if 'image' in ele:
            ratio = ele['image']['image_info']['ratio']
            if ratio <= 1 and (ele['image']['image_info']['width'] < 320 or ele['image']['image_info']['height'] < 480):
                return False
            elif ratio > 1 and (
                            ele['image']['image_info']['width'] < 480 or ele['image']['image_info']['height'] < 320):
                return False
            elif not self.meitu_ratio_floor_limit <= ratio <= self.meitu_ratio_ceil_limit:
                return False
            else:
                return True
        else:
            return True
