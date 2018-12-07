# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class TagsMaker(MapMiddleware):

    raw_tags_hot = [
        u'热点',
    ]

    def process(self, item):
        item['tags'] = item['raw']['tags']
        item['model_version'] = item['raw']['model_version']
        tags = [x[0] for x in item['tags']]
        raw_tags = item['raw_tags']
        if u'图集' not in tags and u'图集' in raw_tags:
            img_num = self.get_img_num(item)
            if img_num > 5:
                item['tags'].append([u'图集', 1.0])
        if u'触宝_美图' not in tags and u'触宝_美图' in raw_tags:
            item['tags'].append([u'触宝_美图', 1.0])
        if u'触宝_视频' in tags:
            item['tags'] = filter(lambda t: t[0] != u'触宝_视频', item['tags'])
            if u'视频' not in tags:
                item['tags'].append([u'视频', 1.0])
        if u'热门' not in tags:
            for raw_tag_hot in self.raw_tags_hot:
                if raw_tag_hot in raw_tags:
                    item['tags'].append([u'热门', 1.0])
                    break
        return item

    def get_img_num(self, item):
        content = item['raw']['content']
        num = 0
        for element in content:
            if 'image' in element:
                num += 1
        return num
