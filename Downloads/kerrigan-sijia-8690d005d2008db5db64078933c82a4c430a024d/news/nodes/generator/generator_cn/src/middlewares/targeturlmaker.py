# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
from urlparse import urljoin


class TargetUrlMaker(MapMiddleware):

    def __init__(self, *a, **kw):
        super(TargetUrlMaker, self).__init__(*a, **kw)
        self.aliyun_server = self.settings['ALIYUN_SERVER']

    def process(self, item):
        item['target_url'] = urljoin(self.aliyun_server, item['raw']['url']['target_url'])
        return item
