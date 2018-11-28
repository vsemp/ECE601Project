# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware


class ContentFilter(FilterMiddleware):
    def __init__(self, *a, **kw):
        super(ContentFilter, self).__init__(*a, **kw)
        self.bad_words = [
            u'版权声明',
            u'卫生棉条',
            u'Δ长按二维码“识别”关注',
            u'三级电影',
            u'六合彩',
            u'电话投注',
            u'先奸后杀',
            u'未完待续',
            u'阅读原文',
            u'戳原文'
        ]
        self.live_title = [
            u'互动直播',
            u'正在直播',
            u'正直播',
            u'全景直播',
        ]
        self.live_content = [
            u'视频直播',
            u'图文直播',
            u'文字直播',
            u'直播间',
        ]
        self.album_width_floor = 240
        self.ratio_floor_limit = float(9) / 16
        self.ratio_ceil_limit = float(16) / 9

    def process(self, item):
        return self.process_for_all(item) and \
               self.process_for_album(item) and \
               self.process_for_meitu(item)

    def process_for_all(self, item):
        account = item['account']
        content = item['content']
        for bad_word in self.bad_words:
            if bad_word in content:
                if item['raw']['subtitle'].startswith('ugc'):
                    if bad_word == u'版权声明':
                        continue
                # filter the whole item
                self.filter_standard_log(account)
                return False
        if not self.live_filter(item):
            self.filter_standard_log(account)
            return False
        return True

    def live_filter(self, item):
        if u'直播' not in item['raw']['title']:
            return True
        for word in self.live_title:
            if word in item['raw']['title']:
                return False
        tags = [x[0] for x in item['tags']]
        if u'体育' in tags or u'热门' in tags:
            for word in self.live_content:
                if word in item['content']:
                    return False
        return True

    def process_for_album(self, item):
        account = item['raw']['account']
        if u'图集' in item['raw']['raw_tags']:
            for ele in item['raw']['content']:
                if 'image' in ele:
                    img_width = ele['image']['image_info']['width']
                    if img_width < self.album_width_floor:
                        self.filter_standard_log(account, 'img_width %s' % img_width)
                        return False
            return True
        else:
            return True

    def process_for_meitu(self, item):
        if u'触宝_美图' in item['raw']['raw_tags']:
            image_count = len([ele for ele in item['raw']['content'] if 'image' in ele])
            if image_count == 0:
                account = item['raw']['account']
                self.filter_standard_log(account, 'all picture filtered because of ratio')
                return False
            else:
                return True
        else:
            return True
