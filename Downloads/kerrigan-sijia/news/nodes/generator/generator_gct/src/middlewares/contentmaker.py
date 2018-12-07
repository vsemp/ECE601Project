# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import re
import copy


class ContentMaker(MapMiddleware):
    def __init__(self, *a, **kw):
        super(ContentMaker, self).__init__(*a, **kw)
        self.invalid_pattern = [
            re.compile(u'({([-_\s\w]*:[^;]*;)+})'),  # CSS codes
            re.compile(u'var\s+\w+'),  # JavaScript codes
            re.compile(u'((?i)</?[a-z][-:\.a-z0-9]*(?=[\s>])(\'[^\']*\'|"[^"]*"|[^\'">])*>)'),  # HTML tags
        ]
        # 需要过滤掉的文章行（包含需要过滤的文章段落）
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
        return self.process_for_all(item)

    def process_for_all(self, item):
        if item['raw']['page_type'] == "out_link_news":
            item['content'] = []
            return item
        if item['raw']['article_class'] != 2:
            return item
        if item['raw']['content_type'] != "news":
            return item
        if 'content' not in item['raw'] or not item['raw']['content']:
            self.logger.info("content is None!!!!!!")
            item['need_filter'] = True
            item['filter_reason'] = "content is None"
            return item
        raw = item['raw']
        contents = []
        word_ch = 0
        word = 0
        count_image = 0

        for element in raw['content']:
            text = element['text'] if 'text' in element else ''
            # TODO 过滤需要对rich_content进行处理
            rich_content = element['rich_content'] if 'rich_content' in element else ''

            # if not self.detect_invalid_pattern(text):
            #     contents = []
            #     self.logger.info("ContentMaker invalid_pattern!!!!!!")
            #     break
            # # 判断是否包含中文
            # m = re.findall(ur'[\u4e00-\u9fa5]+', text)
            # text_norm = ''.join(m)
            # if text_norm in self.sign_related:
            #     # stop adding more elements, ie, filter subsequent elements
            #     break

            # 过滤无效行
            if 'image' not in element or not element['image'] or element['image'] == 'None':
                if not text and not rich_content:
                    # filter this meaningless element
                    continue
            else:
                if 'image_info' not in element:
                    item['need_filter'] = True
                    item['filter_reason'] = "image_info is None"
                    self.logger.error(element)
                    self.logger.error("image_info is None !!!")
                    break
                count_image += 1
                element['image'] = dict()
                element['image']['image_info'] = element['image_info']
                element['image']['url'] = element['image_info']['url']
                element.pop('image_info')
            need_filter = False
            for bad_start in self.bad_starts:
                if text.startswith(bad_start):
                    need_filter = True
                    break
            if need_filter:
                self.logger.info("ContentMaker need_filter lines !!!!!!")
                continue
            contents.append(element)
            for character in text:
                if 0x4e00 <= ord(character) <= 0x9fa5:
                    word_ch += 1
            word += len(text)
        item['content'] = contents
        item['count_image'] = count_image
        return item

    def detect_invalid_pattern(self, text):
        for invalid_pattern in self.invalid_pattern:
            m = invalid_pattern.search(text)
            if m:
                return False
        return True
