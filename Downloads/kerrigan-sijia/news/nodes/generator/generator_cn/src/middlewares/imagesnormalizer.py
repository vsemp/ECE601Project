# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware


class ImagesNormalizer(MapMiddleware):
    def __init__(self, *a, **kw):
        super(ImagesNormalizer, self).__init__(*a, **kw)
        self.aliyun_server = self.settings['ALIYUN_SERVER']

    def process(self, item):
        if u'触宝_美图' in item['raw']['raw_tags'] or u'触宝_图集' in item['raw']['raw_tags']:
            #print "###", item
            self.process_for_meitu(item)
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
                item['small_img_url'] = '%s/news/%s/img/%s@' % (
                    self.aliyun_server,
                    pubdate,
                    item['small_image']['norm_name'])
                resize_info = item['small_image'].get('resize_info', None)
                if resize_info:
                    item['small_img_url'] += '%s-%s-%s-%sa|' % (
                        resize_info['point_w'],
                        resize_info['point_h'],
                        resize_info['width'],
                        resize_info['height'])
                item['small_img_url'] += '192w_144h_90Q_150sh'
            else:
                item['small_img_url'] = ''
            if item['large_image']:
                item['large_img_url'] = '%s/news/%s/img/%s@' % (
                    self.aliyun_server,
                    pubdate,
                    item['large_image']['norm_name'])
                resize_info = item['large_image'].get('resize_info', None)
                if resize_info:
                    item['large_img_url'] += '%s-%s-%s-%sa|' % (
                        resize_info['point_w'],
                        resize_info['point_h'],
                        resize_info['width'],
                        resize_info['height'])
                item['large_img_url'] += '584w_278h_90Q_150sh'
            else:
                item['large_img_url'] = ''
            del item['small_image']
            del item['large_image']
            if 'album_image' in item:
                item['album_img_url'] = []
                for album_image in item['album_image']:
                    if not album_image:
                        continue
                    item['album_img_url'].append('%s/news/%s/img/%s@192w_144h_90Q_150sh'
                                                 % (self.aliyun_server,
                                                    pubdate,
                                                    album_image['norm_name']))
                del item['album_image']
                if len(item['album_img_url']) != 3:
                    del item['album_img_url']
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
