# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
import json


class ImagesRecall(MapMiddleware):

    def __init__(self, *a, **kw):
        super(ImagesRecall, self).__init__(*a, **kw)
        self.image_look_table = self.settings['IMAGE_LOOK_TABLE']
        self.recall_keys = [
            'small_img_url',
            'large_img_url',
            'album_img_url',
        ]

    def process(self, item):
        if item['need_upload']:
            recall = {}
            for key in self.recall_keys:
                if item.get(key):
                    recall[key] = item[key]
            item['recall'] = json.dumps(recall, ensure_ascii=False, encoding='utf8', sort_keys=True).encode('utf8')
            return item
        account = item['account']
        recall = self.redis_cli.hget(self.image_look_table, account)
        if not recall:
            item['recall'] = None
            return item
        recall = json.loads(recall)
        for key in self.recall_keys:
            if recall.get(key):
                item[key] = recall[key]
        item['recall'] = None
        return item
