# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
from src.util.image_util import select_thumbnails


class ImagesMaker(MapMiddleware):
    meitu_cover_ceil_limit = 2

    def process(self, item):

        if 'content_type' in item and item['content_type'] == 'news':
            if "thumbnails" in item['raw'] and len("thumbnails") != 0:
                item['thumbnails'] = item['raw']['thumbnails']

        if item['need_upload']:
            item['small_image'] = self.get_what_image(item, 'small')
            if item.get('video'):
                item['large_image'] = self.get_what_image(item, 'large')
            else:
                item['large_image'] = self.get_what_image(item, 'large')
            item['album_image'] = self.get_album_image(item)
            item['share_image'] = self.get_what_image(item, 'share')
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

    def get_what_image(self, item, cat='share'):
        for thumbnail in item['raw'].get('thumbnails', []):
            image_name = thumbnail.get('image_info', {}).get('norm_name', None)
            if cat in image_name.lower():
                return thumbnail
        return {}

    def get_album_image(self, item):
        invalid_format = ['GIF']
        thumbnails = []
        for thumbnail in item['raw'].get('thumbnails', []):
            image_format = thumbnail.get('image_info', {}).get('format', None)
            image_qrcode = thumbnail.get('image_info', {}).get('qr_code', True)
            image_name = thumbnail.get('image_info', {}).get('norm_name', '')
            if 'share' in image_name.lower() or 'large' in image_name.lower():
                continue
            if not image_qrcode and image_format and \
                            image_format not in invalid_format:
                thumbnails.append(thumbnail)
        if len(thumbnails) >= 3:
            return thumbnails[:3]
        else:
            return []

    def gen_images_to_upload(self, item):
        images = []
        if 'content_type' in item and item['content_type'] == 'news':
            for thumbnail in item['raw'].get('thumbnails', []):
                images.append(thumbnail)
            for element in item['content']:
                if not 'image' in element or element['image'] == '':
                    continue
                image_package = element['image']
                images.append(image_package)

        small_image = item['small_image']
        if small_image and small_image not in images:
            images.append(small_image)
        share_image = item['share_image']
        if share_image and share_image not in images:
            images.append(share_image)
        large_image = item['large_image']
        if large_image and large_image not in images:
            images.append(large_image)
        for image_package in item['album_image']:
            if image_package not in images:
                images.append(image_package)
        return images
