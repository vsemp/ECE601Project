# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
from urlparse import urljoin

# regions
REGION_CHINA = 'china'
REGION_ASIA = 'asia'
REGION_AMERICA = 'america'
REGION_EUROPE = 'europe'
REGION_GCT = 'gct'


class TargetUrlMaker(MapMiddleware):
    def __init__(self, *a, **kw):
        super(TargetUrlMaker, self).__init__(*a, **kw)
        self.aliyun_server_ap = 'http://news.ap.cdn.cootekservice.com'
        self.aliyun_server_eu = 'http://news.eu.cdn.cootekservice.com'
        self.aliyun_server_usa = 'http://news.usa.cdn.cootekservice.com'
        self.aliyun_server = ''

    def process(self, item):
        if item['region'] == REGION_ASIA:
            self.aliyun_server = self.aliyun_server_ap
        elif item['region'] == REGION_AMERICA:
            self.aliyun_server = self.aliyun_server_usa
        elif item['region'] == REGION_EUROPE:
            self.aliyun_server = self.aliyun_server_eu
        item['target_url'] = urljoin(self.aliyun_server, item['raw']['url']['target_url'])
        return item


class ImagesNormalizer(MapMiddleware):
    def __init__(self, *a, **kw):
        super(ImagesNormalizer, self).__init__(*a, **kw)
