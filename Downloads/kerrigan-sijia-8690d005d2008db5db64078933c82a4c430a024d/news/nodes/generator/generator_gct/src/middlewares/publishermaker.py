# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware

# regions
REGION_CHINA = 'china'
REGION_ASIA = 'asia'
REGION_AMERICA = 'america'
REGION_EUROPE = 'europe'
REGION_GCT = 'gct'


class PublisherMaker(MapMiddleware):
    def __init__(self, *a, **kw):
        super(PublisherMaker, self).__init__(*a, **kw)
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

        item['publisher'] = item['raw'].get('publisher', "")
        item['publisher_id'] = item['raw'].get('publisher_id', "")
        item['publisher_icon'] = item['raw'].get('publisher_icon', "")
        # TODO(xinyu.du@cootek.cn) 换到其他位置
        item['input_type'] = item['raw'].get('input_type', "")

        pubdate = item['pubdate']
        if item['publisher_icon']:
            item['publisher_icon_url'] = '%s/news/icon/%s' % (
                self.aliyun_server,
                item['publisher_icon']['norm_name'])

        return item
