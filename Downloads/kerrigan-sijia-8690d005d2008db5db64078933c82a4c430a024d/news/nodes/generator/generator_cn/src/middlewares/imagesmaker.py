# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
from src.util.image_util import select_thumbnails


class ImagesMaker(MapMiddleware):
    meitu_cover_ceil_limit = 2

    def process(self, item):
        if u'触宝_美图' in item['raw']['raw_tags'] or u'触宝_图集' in item['raw']['raw_tags']:
            self.process_for_meitu(item)
        else:
            if item['need_upload']:
                item['small_image'] = self.choose_fit_img(item, 'small')
                if item.get('video'):
                    item['large_image'] = self.choose_fit_img(item, 'video')
                else:
                    item['large_image'] = self.choose_fit_img(item, 'large')
                item['album_image'] = self.get_album_image(item)
                item['images'] = self.gen_images_to_upload(item)
            else:
                item['small_image'] = {}
                item['large_image'] = {}
                item['album_image'] = []
                item['images'] = []
        return item

    def choose_fit_img(self, item, requirement='small'):
        raw = item['raw']
        thumbnails = raw.get('thumbnails', [])
        image_package = select_thumbnails(requirement, thumbnails)
        if image_package:
            return image_package
        if requirement != 'small':
            return {}
        images = []
        element = {}
        for element in raw['content']:
            if 'image' in element:
                images.append(element['image'])
        if element and 'image' in element:
            images.pop()
        image_package = select_thumbnails(requirement, images)
        if image_package:
            return image_package
        return {}

    def get_album_image(self, item):
        invalid_format = ['GIF']
        thumbnails = []
        for thumbnail in item['raw'].get('thumbnails', []):
            image_format = thumbnail.get('image_info', {}).get('format', None)
            image_qrcode = thumbnail.get('image_info', {}).get('qr_code', True)
            if not image_qrcode and image_format and \
                            image_format not in invalid_format:
                thumbnails.append(thumbnail)
        if len(thumbnails) >= 3:
            return thumbnails[:3]
        else:
            return []

    def gen_images_to_upload(self, item):
        images = []
        for element in item['raw']['content']:
            if not 'image' in element:
                continue
            image_package = element['image']
            images.append(image_package)
        small_image = item['small_image']
        if small_image and small_image not in images:
            images.append(small_image)
        large_image = item['large_image']
        if large_image and large_image not in images:
            images.append(large_image)
        for image_package in item['album_image']:
            if image_package not in images:
                images.append(image_package)
        return images

    def process_for_meitu(self, item):
        if item['raw'].get('thumbnails', []):
            item['cover_image'] = item['raw']['thumbnails']
            item['images'] = [ele['image']
                              for ele in item['raw']['content']
                              if 'image' in ele]
            item['images'].append(item['cover_image'][0])
        else:
            item['images'] = [ele['image']
                              for ele in item['raw']['content']
                              if 'image' in ele]
            item['cover_image'] = item['images'][:self.meitu_cover_ceil_limit]