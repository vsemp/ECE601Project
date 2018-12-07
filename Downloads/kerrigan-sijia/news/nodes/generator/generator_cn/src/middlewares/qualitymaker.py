# -*- coding: utf-8 -*-
import os
from src.middlewares.base import MapMiddleware
import logging

'''
inewsweek 238 中国新闻周刊
huxiu 215 虎嗅网
news36kr 214 36氪
bjnews 237 新京报
miuimeinv 412 小米美女视频
'''

source_list_1 = ('238', '215', '214', '237', '412')
source_list_2 = set()
source_list_3 = set()
source_list_4 = set()
source_list_5 = set()
source_list_6 = ('211', '210', '213', '249')

class QualityMaker(MapMiddleware):

    def __init__(self, *a, **kw):
        super(QualityMaker, self).__init__(*a, **kw)

    def process(self, item):
        with open(self.get_resource_file_path('quality/weixin1'), 'r') as f:
            for line in f:
                source_list_2.add(line.replace('\n', '').decode('utf-8'))

        with open(self.get_resource_file_path('quality/weixin2'), 'r') as f:
            for line in f:
                source_list_3.add(line.replace('\n', '').decode('utf-8'))

        with open(self.get_resource_file_path('quality/toutiao1'), 'r') as f:
            for line in f:
                source_list_4.add(line.replace('\n', '').decode('utf-8'))

        with open(self.get_resource_file_path('quality/toutiao2'), 'r') as f:
            for line in f:
                source_list_5.add(line.replace('\n', '').decode('utf-8'))
        account = item['account']
        subtitle = item['subtitle']
        acc = account.split('-')[0]
        if acc.startswith('9') or acc in source_list_1:
            item['quality'] = 1
            return item
        if acc in source_list_6:
            item['quality'] = 3
            return item
        if acc.startswith('3'):
            if subtitle in source_list_4:
                item['quality'] = 1
            elif subtitle in source_list_5:
                item['quality'] = 2
            else:
                if item['comment_count'] >= 100:
                    item['quality'] = 1
                elif item['comment_count'] >= 50:
                    item['quality'] = 2
                else:
                    item['quality'] = 3
            return item
        if acc.startswith('1'):
            if subtitle in source_list_2:
                item['quality'] = 1
            elif subtitle in source_list_3:
                item['quality'] = 2
            else:
                if item['hit_count'] >= 50000:
                    item['quality'] = 1
                elif item['hit_count'] >= 10000:
                    item['quality'] = 2
                else:
                    item['quality'] = 3
            return item
        if acc.startswith('4'):
            if acc in ['49']:
                if item['hit_count'] >= 200000:
                    item['quality'] = 1
                elif item['hit_count'] >= 20000:
                    item['quality'] = 2
                else:
                    item['quality'] = 3
            elif acc in ['44']:
                if item['comment_count'] >= 100:
                    item['quality'] = 1
                elif item['comment_count'] >= 50:
                    item['quality'] = 2
                else:
                    item['quality'] = 3
            elif acc in ['46', '413']:
                item['quality'] = 3
            else:
                item['quality'] = 2
            return item
        item['quality'] = 2
        return item
