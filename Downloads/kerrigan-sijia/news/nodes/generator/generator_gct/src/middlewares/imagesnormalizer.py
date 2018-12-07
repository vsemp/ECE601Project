# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware

# regions
REGION_CHINA = 'china'
REGION_ASIA = 'asia'
REGION_AMERICA = 'america'
REGION_EUROPE = 'europe'
REGION_GCT = 'gct'


class ImagesNormalizer(MapMiddleware):
    def __init__(self, *a, **kw):
        super(ImagesNormalizer, self).__init__(*a, **kw)
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
        if not item:
            return

        if item['content_type'] == "news":
            # print "###", item
            self.process_for_news(item)
            pubdate = item['pubdate']
            item['small_img_url'] = ''
            item['large_img_url'] = ''
            if 'share_image' in item:
                try:
                    item['share_img_url'] = '%s/news/%s/img/%s' % (
                        self.aliyun_server,
                        pubdate,
                        item['share_image']['norm_name'])
                except Exception, e:
                    item['share_img_url'] = None
                del item['share_image']
        else:
            if not item['need_upload']:
                del item['small_image']
                del item['large_image']
                del item['album_image']
                item['small_img_url'] = ''
                item['large_img_url'] = ''
                return item
            pubdate = item['pubdate']
            if item['small_image']:
                item['small_img_url'] = '%s/news/img/%s' % (
                    self.aliyun_server,
                    item['small_image']['norm_name'])
            else:
                item['small_img_url'] = ''
            if item['large_image']:
                item['large_img_url'] = '%s/news/img/%s' % (
                    self.aliyun_server,
                    item['large_image']['norm_name'])
            else:
                item['large_img_url'] = ''
            del item['small_image']
            del item['large_image']
            if 'album_image' in item:
                item['album_img_url'] = []
                for album_image in item['album_image']:
                    if not album_image:
                        continue
                    item['album_img_url'].append('%s/news/%s/img/%s'
                                                 % (self.aliyun_server,
                                                    pubdate,
                                                    album_image['norm_name']))
                del item['album_image']
                if len(item['album_img_url']) != 3:
                    del item['album_img_url']
            if 'share_image' in item:
                try:
                    item['share_img_url'] = '%s/news/%s/img/%s' % (
                        self.aliyun_server,
                        pubdate,
                        item['share_image']['norm_name'])
                except Exception, e:
                    item['share_img_url'] = None
                del item['share_image']
        return item

    def process_for_meitu(self, item):
        item['cover_img_url'] = []
        for cover_image in item['cover_image']:
            if cover_image['image_info'].get('size') > 200000:
                item['cover_img_url'].append(
                    ('%s/news/%s/img/%s@%sw_%sh_35Q'
                     % (self.aliyun_server,
                        item['pubdate'],
                        cover_image['norm_name'],
                        int(cover_image['image_info']['width']),
                        int(cover_image['image_info']['height']))))
            else:
                item['cover_img_url'].append(
                    ('%s/news/%s/img/%s@%sw_%sh_90Q'
                     % (self.aliyun_server,
                        item['pubdate'],
                        cover_image['norm_name'],
                        int(cover_image['image_info']['width']),
                        int(cover_image['image_info']['height']))))
        del item['cover_image']
        item['large_img_url'] = item['cover_img_url'][0]
        item['small_img_url'] = ''

    def process_for_news(self, item):
        for each in item['thumbnails']:
            each['url'] = '%s/news/img/%s' % (
                self.aliyun_server,
                each['image_info']['norm_name'])

        for each in item['content']:
            if 'image' not in each or each['image'] == '':
                continue
            each['image']['url'] = '%s/news/img/%s' % (
                self.aliyun_server,
                each['image']['image_info']['norm_name'])
